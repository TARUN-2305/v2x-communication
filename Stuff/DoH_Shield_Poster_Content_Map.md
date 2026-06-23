# DoH-Shield Poster — Content Map
## Direct replacement guide for the RVCE poster template (AaaS Labs layout)

Go through this top to bottom — it follows the exact panel order in your template.

---

## HEADER

**Replace:**
- College name: keep as-is — "RV College of Engineering, Bengaluru – 560059."
- **Title:** `DoH-Shield: Cluster-Aware Traffic Morphing with Differential Privacy for DNS-over-HTTPS Website Fingerprinting Resistance`
- **Authors:** `Tanmay Dev D | Tarun R | Tejasvi Vasant Hegde`
- **USNs:** `1RV23CS269 | 1RV23CS271 | 1RV23CS272`

---

## INTRODUCTION

Replace the AaaS paragraph with:

> DoH-Shield is a client-side privacy defense for DNS-over-HTTPS (DoH). While DoH encrypts DNS queries to stop eavesdropping, the encrypted traffic still leaks observable metadata — packet sizes, timing gaps, and query counts — that lets a passive network attacker identify which website a user visited with over 99% accuracy. DoH-Shield is a local proxy that morphs this traffic using cluster-based dummy query injection and differential privacy, reducing attacker accuracy to near-random while proving a formal mathematical privacy guarantee.

---

## PROBLEM DEFINITION

Replace the AaaS bullet list with:

> Modern DoH deployments (Cloudflare, Google, Firefox, Chrome) encrypt DNS query *content* but not connection *metadata* — and this gap is actively exploited.

1. A Random Forest classifier achieves **F₁ = 0.9999** and a Deep Fingerprinting CNN achieves **F₁ = 0.9989** at identifying visited websites from encrypted DoH traffic alone — no decryption needed.
2. Existing padding standards (RFC 8467) leave timing and packet-count signatures untouched, achieving negligible accuracy reduction (~95% attacker accuracy remains).
3. Prior obfuscation defenses (Panchenko 2022) reduce attacker accuracy to ~9% but require ~80% extra bandwidth and offer **no formal guarantee** — an adaptive attacker who retrains can recover accuracy.
4. The only defense with a formal guarantee (Adaptive Tamaraw 2025) requires **~200% bandwidth overhead** — impractical for real browsing.
5. No existing client-side defense combines a provable privacy bound, sub-40% overhead, and resistance to adaptive retraining — **this is the gap DoH-Shield closes.**

---

## OBJECTIVES

Replace the AaaS numbered list with:

1. Replicate two published website-fingerprinting attacks (Random Forest and Deep Fingerprinting CNN) on the CIRA-CIC-DoHBrw-2020 dataset and confirm baseline attacker F₁ ≥ 0.99.
2. Build a K-Means cluster-aware morphing engine (K=30) that injects EDNS(0)-padded dummy DoH queries to morph each flow toward its cluster centroid.
3. Introduce **Diverse-Neighbor Merging** — a hardening step that eliminates pure clusters and guarantees k-anonymity (k_min = 343).
4. Implement a Differential Privacy timing-noise layer (Laplace Mechanism, ε = 1.0) and formally prove P_attack ≤ 1/k_min + e⁻ε = 37.08%.
5. Deploy a working client-side mitmproxy proxy with adaptive session-key randomization, a live dashboard, and a 4-point automated test suite — verified, open-source.

---

## METHODOLOGY (the 6-step numbered flowchart)

The AaaS template has a **vertical 6-box numbered flowchart** (Requirements Collection → Workflow Creation → ... → Report Generation). Replace each box's title and bullets exactly as below — keep the same colored-box style and numbering 1–6.

**Box 1 — Dataset & Feature Extraction**
- CIRA-CIC-DoHBrw-2020: 268,661 DoH flows
- 29 statistical features per flow (DoHMeter)
- 13:1 class imbalance handled via balanced weighting

**Box 2 — Attack Model Training**
- Random Forest (200 trees) → F₁ = 0.9999
- Deep Fingerprinting CNN (40 epochs, T4 GPU) → F₁ = 0.9989
- Feature importance: PacketLengthMode = 22.63%

**Box 3 — K-Means Clustering**
- K = 30 clusters (k-means++, elbow-validated)
- PCA confirms natural behavioral structure
- Inertia = 1,115,151

**Box 4 — Diverse-Neighbor Merging**
- 9 pure clusters detected (privacy leak, l=1)
- Remapped to nearest diverse neighbor
- Result: 0 pure clusters, k_min = 343

**Box 5 — Proxy Construction (DoH-Shield)**
- mitmproxy intercepts live DoH sessions
- Adaptive session-key cluster randomization
- Laplace DP noise on timing gaps (ε=1.0)
- Async EDNS(0) dummy query injection

**Box 6 — Evaluation**
- CNN attacker: F₁ 0.9989 → 0.1044
- Bandwidth overhead < 40%
- Formal bound verified empirically

---

## TOOLS USED

The AaaS template has an icon grid with categories (Frontend / Backend / Security Tools / AI / DevOps). Replace categories and items as follows — keep same icon-grid visual style:

**Category 1 — Core & Networking**
- Python 3.12/3.14
- mitmproxy 10.x
- dnspython
- httpx (async)

**Category 2 — Machine Learning**
- scikit-learn (K-Means, Random Forest)
- PyTorch (Deep Fingerprinting CNN)
- scipy (Laplace DP noise)

**Category 3 — Data & Visualization**
- NumPy / Pandas
- Matplotlib / Seaborn
- Rich (live terminal dashboard)

**Category 4 — Infrastructure**
- Google Colab (Tesla T4 GPU)
- Ubuntu 22.04 LTS
- Git / GitHub (open source)

**Bottom banner text** (replacing "Built for Security..."):
> Built for Privacy. Formally proven, empirically verified, and fully reproducible — open source at github.com/TARUN-2305/DoH-Sheild

---

## RESULTS AND DISCUSSIONS

### Top "KEY RESULTS" icon row (6 boxes in AaaS — keep 6, replace each)

| Icon box | Big number | Label |
|---|---|---|
| 1 | **0.1044** | CNN Attacker F₁ (from 0.9989) |
| 2 | **89.5%** | Relative Attack Reduction |
| 3 | **<40%** | Bandwidth Overhead |
| 4 | **37.08%** | Formal Privacy Bound (P_attack ≤) |
| 5 | **343** | k-Anonymity (k_min, was 3) |
| 6 | **4/4** | Automated Tests Passing |

### "RESULT HIGHLIGHTS" bar chart

Replace the AaaS bar chart (Module Integration, Workflow Automation, etc.) with a **5-bar comparison chart** — Attacker F₁ across defenses:

| Bar | Value |
|---|---|
| Undefended (RF) | 99.99% |
| Undefended (CNN) | 99.89% |
| RFC 8467 Padding | ~95% |
| Panchenko 2022 | ~9% |
| **DoH-Shield (CNN)** | **10.44%** |

(Lower = better defense — you can add a horizontal dashed line at 15% labeled "Security Threshold")

### "DISCUSSIONS" box

Replace AaaS discussion bullets with:

- Cluster-aware morphing exploits natural similarity between websites — attacker can only narrow down to a cluster, not a single site
- The formal bound (37.08%) holds for **any** classifier, including ones that retrain on defended traffic
- RF attacker (relies on PacketLengthMode) is harder to reduce than CNN — mode-targeted injection is identified as future work
- DoH-Shield requires zero server-side changes — deployable today by any user

### "Overall Outcome" line at the bottom

> DoH-Shield delivers a formally proven, empirically validated, client-only DNS privacy defense that closes the gap between provable security and practical bandwidth cost.

---

## CONCLUSIONS

Replace the AaaS paragraph with:

> DoH-Shield demonstrates that cluster-aware traffic morphing, differential privacy timing noise, and adaptive session-key randomization can be combined into a single client-side defense that is both formally provable and practically deployable. By introducing Diverse-Neighbor Merging to harden K-Means clusters and proving P_attack ≤ 1/k_min + e⁻ε = 37.08%, the system reduces a state-of-the-art Deep Fingerprinting CNN attacker from F₁ = 0.9989 to F₁ = 0.1044 — an 89.5% reduction — at under 40% bandwidth overhead, without requiring any changes to DoH resolvers or servers.

---

## OUTCOME OF THE WORK

Replace the AaaS paragraph with:

> A fully functional, open-source client-side proxy (six Python modules) running on Ubuntu 22.04, built on mitmproxy, that intercepts live DoH sessions, computes 29 CIRA statistical features in real time, assigns flows to one of 30 hardened K-Means clusters via adaptive session-key randomization, applies Laplace-mechanism differential privacy noise (ε=1.0) to timing gaps, and asynchronously injects EDNS(0)-padded dummy queries — all monitored through a live Rich terminal dashboard and verified by a 4-point automated test suite (all passing). Source available at github.com/TARUN-2305/DoH-Sheild.

---

## REFERENCES

Replace the 5 AaaS references with:

```
[1] P. Hoffman and P. McManus, "DNS Queries over HTTPS (DoH)," IETF RFC 8484, 2018.
[2] A. Panchenko et al., "Toward practical defense against traffic analysis 
    attacks on encrypted DNS traffic," Computers & Security, vol. 119, 2022.
[3] P. Sirinam et al., "Deep Fingerprinting: Undermining Website Fingerprinting 
    Defenses with Deep Learning," ACM CCS 2018.
[4] C. Dwork et al., "Calibrating Noise to Sensitivity in Private Data 
    Analysis," TCC 2006.
[5] S. Khajavi and J. Wang, "Lightening the Load: A Cluster-Based Framework 
    for Website Fingerprinting Defense," arXiv:2509.01046, 2025.
```

---

## MENTOR

Keep the same line, only the name stays identical:

> Prof. Savitri Kulkarni, Assistant Professor, Department of CSE, RVCE

(Note: AaaS template says "Professor" — yours should say **"Assistant Professor"** per your synopsis records.)

---

## IMAGE/FIGURE PLACEMENTS

Your template has image placeholders inside **Tools Used**, **Methodology**, and **Results** panels (the AaaS icon grids/charts). If you'd rather use real chart images instead of redrawing Canva icon-grids, use these from your paper's figure set in this priority order:

| Panel | Best figure to drop in |
|---|---|
| Methodology (visual area) | `cluster_visualization.png` (K-Means + PCA, K=30) |
| Results (visual area) | `cnn_training_curves.png` (loss/accuracy convergence) |
| Results (secondary, if space) | `rf_attack_results.png` (confusion matrix + ROC) |
| Introduction (if you add one) | `rf_feature_importance.png` (shows the attack works) |

All four are embedded in your `DoH_Shield_Paper.pdf` (Figures 1, 5, 6, 7) — screenshot/crop them at high resolution for Canva.

---

## QUICK CHECKLIST

- [ ] Header: title, 3 authors, 3 USNs
- [ ] Introduction paragraph
- [ ] Problem Definition (5 points)
- [ ] Objectives (5 points)
- [ ] Methodology (6 boxes, keep numbering/colors)
- [ ] Tools Used (4 categories + banner)
- [ ] Results: 6 KPI boxes + bar chart + discussion bullets + outcome line
- [ ] Conclusions paragraph
- [ ] Outcome of the work paragraph
- [ ] References (5, renumbered)
- [ ] Mentor line (fix "Assistant Professor")
- [ ] Drop in 2 figures (methodology + results panels)
