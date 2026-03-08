# Demo: Data Injection Examples

Use these two customers and inputs in the **Data Injection Flow** (Monitor → red "Data Injection Flow" button) to show **anomaly** vs **normal** behaviour and how the app flags risk.

---

## Customer 1: Anomaly (High / Medium risk)

**User:** **Fatima Noor** (`AE-USER-004`)  
**Profile:** Low income, Student, UAE. Historical countries: AE only.


| Field                      | Value                     | Why                                                               |
| -------------------------- | ------------------------- | ----------------------------------------------------------------- |
| **Target user**            | AE-USER-004 (Fatima Noor) | Low-income user; large or suspicious activity is more notable     |
| **Number of transactions** | 3–5                       | Enough to trigger amount/daily checks                             |
| **Min amount**             | 20000                     | Single tx >> 5× her baseline (~410) → large amount flag (+55 pts) |
| **Max amount**             | 25000                     | Keeps amounts in the same anomalous range                         |
| **Countries**              | KP (North Korea)          | Country not in her history → new country flag (+45 pts)           |


**Optional:** Leave **Variance** empty. Leave **Currency override** empty (or set e.g. USDT if you want).

**Expected result:** Risk **HIGH** (or MEDIUM). Flags typically include:

- Single tx well above 5× average
- New country never seen in history  
Risk score often in the 75–100 range (HIGH band).

---

## Customer 2: No anomaly (CLEAN)

**User:** **Rashid Al-Maktoum** (`AE-USER-001`)  
**Profile:** High income, Engineer, UAE. Historical countries: AE, SA.


| Field                      | Value                           | Why                                               |
| -------------------------- | ------------------------------- | ------------------------------------------------- |
| **Target user**            | AE-USER-001 (Rashid Al-Maktoum) | High-income user with higher baseline             |
| **Number of transactions** | 3                               | Normal small batch                                |
| **Min amount**             | 800                             | Within his typical range (baseline avg ~1247)     |
| **Max amount**             | 1600                            | Within his typical range                          |
| **Countries**              | AE, SA                          | Both in his historical countries → no new country |


**Leave empty:** Variance, Currency override.

**Expected result:** Risk **CLEAN**. No anomaly. Risk score stays low (e.g. 0–24). No material flags; amounts and geography match his baseline.

---

## Quick reference


| Demo           | User              | User ID     | Amount range | Countries | Expected risk    |
| -------------- | ----------------- | ----------- | ------------ | --------- | ---------------- |
| **Anomaly**    | Fatima Noor       | AE-USER-004 | 20000–25000  | KP        | HIGH (or MEDIUM) |
| **No anomaly** | Rashid Al-Maktoum | AE-USER-001 | 800–1600     | AE, SA    | CLEAN            |


---

## Tips for the demo

1. Run **Anomaly** first, then show the same user’s card with updated risk gauge and flags.
2. Run **No anomaly** (Rashid), then show his card still CLEAN.
3. Use **Reset database** (`python scripts/reset_supabase_regulatory.py`) between runs if you want to repeat from a clean state.

