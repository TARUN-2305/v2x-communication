"""
ECO-SYNC V2X — Persistent Storage (PostgreSQL via psycopg2 sync wrapper)
Uses a thread-pool executor to avoid blocking the asyncio event loop.
Falls back silently if DB is unavailable (simulation continues without persistence).
"""
import asyncio
import json
import uuid
from typing import Optional
from loguru import logger

try:
    import psycopg2
    import psycopg2.extras
    _HAS_PSYCOPG = True
except ImportError:
    _HAS_PSYCOPG = False


class Storage:
    def __init__(self, dsn: str):
        self._dsn  = dsn
        self._conn = None
        self._ok   = False

    async def init(self):
        if not _HAS_PSYCOPG or not self._dsn:
            logger.warning("Postgres not configured — running without persistence")
            return
        loop = asyncio.get_event_loop()
        try:
            self._conn = await loop.run_in_executor(
                None,
                lambda: psycopg2.connect(self._dsn, connect_timeout=5)
            )
            self._conn.autocommit = True
            self._ok = True
            logger.info("✅ PostgreSQL connected")
        except Exception as e:
            logger.warning(f"PostgreSQL unavailable ({e}) — running without persistence")

    def _exec(self, sql: str, params=None):
        if not self._ok:
            return
        try:
            with self._conn.cursor() as cur:
                cur.execute(sql, params)
        except Exception as e:
            logger.debug(f"DB write error: {e}")

    async def _async_exec(self, sql, params=None):
        if not self._ok:
            return
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, lambda: self._exec(sql, params))

    # ── Session ────────────────────────────────────────────────────────────────
    async def create_session(self, sid: uuid.UUID, mode: str, num_buses: int):
        await self._async_exec(
            "INSERT INTO sessions (id, mode, num_buses) VALUES (%s, %s, %s)",
            (str(sid), mode, num_buses)
        )

    async def close_session(self, sid: uuid.UUID):
        await self._async_exec(
            "UPDATE sessions SET ended_at=NOW(), status='stopped' WHERE id=%s",
            (str(sid),)
        )

    # ── Metrics ────────────────────────────────────────────────────────────────
    async def save_metrics(self, sid, m: dict):
        if not sid: return
        await self._async_exec(
            """INSERT INTO metrics
               (session_id, tick, mode, avg_headway_s, headway_variance,
                bunching_count, total_decisions, holds, skips, proceeds, passengers_served)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (str(sid), m.get("tick",0), m.get("mode","agentic"),
             m.get("avg_headway_s",0), m.get("variance",0),
             m.get("bunching",0), m.get("decisions",0),
             m.get("holds",0), m.get("skips",0), m.get("proceeds",0),
             m.get("passengers_served",0))
        )

    async def get_metrics(self, sid: Optional[str], limit: int = 60):
        if not self._ok or not sid:
            return []
        loop = asyncio.get_event_loop()
        def _q():
            with self._conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(
                    "SELECT * FROM metrics WHERE session_id=%s ORDER BY ts DESC LIMIT %s",
                    (sid, limit)
                )
                return [dict(r) for r in cur.fetchall()]
        try:
            return await loop.run_in_executor(None, _q)
        except Exception:
            return []

    # ── Decisions ──────────────────────────────────────────────────────────────
    async def save_decision(self, sid, stop, b1, b2, a1, a2, reasoning, model, latency, hw_before, hw_after):
        if not sid: return
        await self._async_exec(
            """INSERT INTO decisions
               (session_id, stop_name, bus_1_id, bus_2_id,
                bus_1_action, bus_2_action, reasoning, llm_model, latency_ms,
                headway_before, headway_after)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (str(sid), stop, b1, b2, a1, a2, reasoning, model, latency, hw_before, hw_after)
        )

    async def get_decisions(self, sid: Optional[str], limit: int = 20):
        if not self._ok or not sid:
            return []
        loop = asyncio.get_event_loop()
        def _q():
            with self._conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(
                    "SELECT * FROM decisions WHERE session_id=%s ORDER BY ts DESC LIMIT %s",
                    (sid, limit)
                )
                return [dict(r) for r in cur.fetchall()]
        try:
            return await loop.run_in_executor(None, _q)
        except Exception:
            return []

    # ── Traffic ────────────────────────────────────────────────────────────────
    async def log_traffic(self, sid, ev: dict):
        if not sid: return
        await self._async_exec(
            "INSERT INTO traffic_events (session_id, location, severity, description) VALUES (%s,%s,%s,%s)",
            (str(sid), ev.get("location",""), ev.get("severity",""), ev.get("desc",""))
        )
