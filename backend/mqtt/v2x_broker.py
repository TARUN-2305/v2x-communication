"""
ECO-SYNC V2X — MQTT V2X Broker Client
Simulates DSRC/C-V2X radio layer using Eclipse Mosquitto.
Topics follow SAE J2735 / ETSI ITS-G5 naming conventions:
  v2x/v2v/{bus_id}/bsm          — Basic Safety Messages
  v2x/v2i/tmc/tim               — Traffic Information Messages (V2I)
  v2x/v2v/debate/{b1}/{b2}      — LLM V2V debate transcripts
  v2x/atis/{stop}               — Passenger information display
"""
import json
import time
from typing import Optional
from loguru import logger

try:
    import paho.mqtt.client as mqtt
    _HAS_MQTT = True
except ImportError:
    _HAS_MQTT = False


class V2XBroker:
    def __init__(self, host: str = "localhost", port: int = 1883):
        self._host = host
        self._port = port
        self._client: Optional[object] = None
        self._connected = False
        self._msg_count = 0

    async def connect(self) -> bool:
        if not _HAS_MQTT:
            logger.warning("paho-mqtt not installed — V2X messages will not be published")
            return False

        def on_connect(client, userdata, flags, rc, props=None):
            if rc == 0:
                self._connected = True
                logger.info(f"📡 MQTT V2X broker connected ({self._host}:{self._port})")
            else:
                logger.warning(f"MQTT connect rc={rc}")

        def on_disconnect(*args, **kwargs):
            self._connected = False
            logger.warning("MQTT disconnected")

        try:
            self._client = mqtt.Client(
                client_id="ecosync_backend",
                protocol=mqtt.MQTTv5,
                callback_api_version=mqtt.CallbackAPIVersion.VERSION2
            )
            self._client.on_connect    = on_connect
            self._client.on_disconnect = on_disconnect
            self._client.connect_async(self._host, self._port, keepalive=60)
            self._client.loop_start()

            import asyncio
            for _ in range(20):
                if self._connected:
                    return True
                await asyncio.sleep(0.3)
            logger.warning("MQTT connection timeout — V2X publishing disabled")
            return False
        except Exception as e:
            logger.warning(f"MQTT unavailable: {e}")
            return False

    async def disconnect(self):
        if self._client:
            self._client.loop_stop()
            self._client.disconnect()

    def publish(self, topic: str, payload: dict, qos: int = 1):
        """Fire-and-forget V2X message publish"""
        if not self._connected or not self._client:
            return
        try:
            self._client.publish(topic, json.dumps(payload), qos=qos)
            self._msg_count += 1
        except Exception as e:
            logger.debug(f"MQTT publish error ({topic}): {e}")

    @property
    def connected(self) -> bool:
        return self._connected

    @property
    def message_count(self) -> int:
        return self._msg_count
