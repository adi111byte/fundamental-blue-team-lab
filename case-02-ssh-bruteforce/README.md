# Case-02: SSH Brute Force Detection via Wazuh

## What Happened
This case simulates the next stage after case-01's reconnaissance: the attacker, having identified an open (though firewall-filtered) SSH service, attempts to gain access through a password brute force attack. Rather than reading `auth.log` manually, detection here relies on Wazuh's log correlation engine, which aggregates failed authentication events from the agent on the target and fires an alert once a threshold is crossed.

- **Status:** [In Progress / Completed]
- **Severity:** High (Credential Access)

## Lab Environment
Full network architecture, addressing, and Wazuh installation steps are documented separately:

**[View Lab Setup](../docs/lab-setup.md)**

**Quick overview:**
- **Attacker:** Kali Linux (`192.168.10.10`) on VMnet2 (LAN)
- **Target:** Ubuntu Server (`192.168.20.10`) on VMnet3 (OPT1), Wazuh agent installed
- **SIEM:** Wazuh Manager (`192.168.10.20`) on VMnet2 (LAN), reached by the agent across pfSense on `1514/tcp` and `1515/tcp`

---

## 1. The Trigger
[FILL IN after running the attack]

- **Timestamp:** [FILL IN]
- **Source IP:** `192.168.10.10` (Kali Linux)
- **Destination:** `192.168.20.10:22` (Ubuntu SSH)
- **Wazuh Rule ID:** [FILL IN — Wazuh ships a default SSH brute force rule, note the exact ID and description shown in the dashboard]
- **Rule Level:** [FILL IN]

> **Why this matters:** A burst of failed authentication attempts against the same account from a single source, within a short window, is not how a human types a password wrong. It's how an automated tool works through a wordlist.

---

## 2. Evidence Collection

### A. Attack Command (Kali)
```bash
hydra -l adi -P small-wordlist.txt ssh://192.168.20.10 -t 4
```
- **Result:** [FILL IN — e.g. number of attempts, whether a valid password was found]

### B. Wazuh Alert (Dashboard)
- **Source:** Wazuh Dashboard > Security Events, filtered to agent `192.168.20.10`
- [FILL IN screenshot + description of the alert entry, including rule ID and match count]

### C. Raw Log Cross-Reference (Ubuntu)
```bash
grep "Failed password" /var/log/auth.log | tail -40 > 02-auth-bruteforce.log
```
- Used to confirm the Wazuh alert matches what actually happened at the OS level, not just what the SIEM inferred.

---

## 3. Reproduction Steps

### Phase 1: Preparation
1. Confirm the Wazuh agent on Ubuntu shows **Active** on the manager dashboard (see `lab-setup.md` for the pre-flight check).
2. Optionally tail the agent log on Ubuntu to watch events in real time:
```bash
   tail -f /var/ossec/logs/ossec.log
```

### Phase 2: Executing the Attack (Kali)
```bash
hydra -l adi -P small-wordlist.txt ssh://192.168.20.10 -t 4
```
- `-l adi`: single known username, lab account created for this purpose
- `-P small-wordlist.txt`: lab-only wordlist, not a real credential dump
- `-t 4`: 4 parallel threads, deliberately modest rather than maximum speed, closer to what a low-and-slow attacker might use to stay under naive rate limits

### Phase 3: Capturing Evidence
1. After Hydra finishes, check the Wazuh dashboard's Security Events for the correlated alert.
2. Pull the matching `auth.log` excerpt from Ubuntu as a cross-reference.
3. Screenshot the Wazuh alert detail (rule ID, level, full log line it matched on).

#### Expected Outcome
A Wazuh alert referencing repeated `sshd` authentication failures from `192.168.10.10`, with a rule ID and level consistent with Wazuh's built-in brute force detection, and an `auth.log` excerpt that lines up with the same timestamps.

---

## 4. Context and Baseline
- **Target:** Ubuntu Server (`192.168.20.10`) running OpenSSH, Wazuh agent active.
- **Network Zone:** OPT1 segment (`192.168.20.0/24`), reached from the LAN segment through pfSense.
- **Normal Behavior:** A handful of failed logins from a known admin mistyping a password is normal. Dozens of failed attempts against the same account within seconds, from a single source, is not.

---

## 5. Deep Dive Analysis
[FILL IN after execution — points to address:]
- Attempt volume and time window: does it match Hydra's `-t 4` thread count and wordlist size?
- Did Wazuh's default threshold trigger correctly, or did it need tuning (too sensitive / not sensitive enough)?
- Cross-check: does every failed attempt in `auth.log` have a corresponding Wazuh event, or did any get missed (indicates event forwarding gaps)?
- Was the correct username (`adi`) present in all attempts, or did the wordlist also include invalid usernames?

---

## 6. MITRE ATT&CK Mapping

| Tactic | Technique ID | Name | Application in This Case |
|---|---|---|---|
| Credential Access | T1110.001 | Brute Force: Password Guessing | Hydra iterated a wordlist against a single known SSH account. |
| Initial Access | T1078 | Valid Accounts | If a password in the wordlist succeeds, the attacker gains a foothold using a legitimate account rather than exploiting a vulnerability. |

> **Tactical Insight:** This picks up directly where case-01 (T1046, Network Service Scanning) left off — the open SSH service found in reconnaissance is exactly what gets targeted here.

---

## 7. Verdict
[FILL IN — Malicious / Suspicious / Benign, with reasoning based on sections 1–5]

---

## 8. Recommended Actions
1. **Immediate block:** Drop or rate-limit `192.168.10.10` at the firewall.
2. **Host hardening:** Consider key-based SSH auth only, disable password login where feasible.
3. **Detection tuning:** Review whether Wazuh's default brute force rule threshold fits this environment — adjust `frequency`/`timeframe` if it fired too late or too early.
4. **Account review:** Confirm the targeted account (`adi`) did not have a successful login during the attack window.

---

## Detection Configuration
[FILL IN — note here whether the default Wazuh SSH brute force rule was used as-is, or whether a custom rule/decoder was added, and why]

---

> **Notes for Future Reference:** This case shows the difference between manually grepping a log file and having a SIEM correlate events automatically. The next step, case-03, moves away from live network attacks and into analyzing phishing domains — a different detection surface entirely (DNS/email, not host or network traffic).
