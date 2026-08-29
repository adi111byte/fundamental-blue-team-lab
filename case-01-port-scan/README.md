# Case-01: Network Reconnaissance and Port Scan Detection

## What Happened
This case simulates a classic pre-attack scenario where an attacker machine running Kali Linux attempts to map out a target Ubuntu server by scanning for open ports. The objective was not to breach the system immediately but to identify active services. Our defense stack, consisting of pfSense and Suricata, detected this activity through TCP handshake anomalies rather than generic signature matches.

-   **Status:** Completed
-   **Severity:** Medium (Reconnaissance / Pre-attack Phase)

## Lab Environment
This case was executed on a custom virtualized lab environment. For detailed network architecture, VM configurations, and pfSense/Suricata setup instructions, please refer to the dedicated infrastructure repository:

 **[View Lab Setup Repository](https://github.com/adi111byte/fundamental-blue-team-lab/blob/main/docs/lab-setup.md)** 
 
**Quick Overview:**
-   **Attacker:** Kali Linux (`192.168.10.10`) connected via VMnet2 (LAN)
-   **Defense:** pfSense Firewall + Suricata IDS (`192.168.10.1` / `192.168.20.1`)
-   **Target:** Ubuntu Server (`192.168.20.10`) connected via VMnet3 (OPT1)

---

## 1. The Trigger
The initial indicator came from Suricata IDS on the pfSense OPT1 interface. Instead of a standard alert, the system flagged stream-level anomalies that reveal the mechanical nature of the scan.

-   **Timestamp:** Aug 29, 2026 at 01:05:20 WIB
-   **Source IP:** `192.168.10.10` (Kali Linux)
-   **Destination:** `192.168.20.10:22` (Ubuntu SSH)
-   **Alert Signature:** `SURICATA STREAM 3way handshake SYN resend different seq on SYN recv`
-   **SID:** `1:2210008` / `1:2210004`

> **Why this matters:** This alert indicates that the scanner was manipulating TCP sequence numbers and leaving handshakes incomplete. Legitimate users logging into SSH do not exhibit this behavior. Automated tools do. This behavioral fingerprint is often more reliable than static signature matching.

---

## 2. Evidence Collection
We gathered proof from three distinct sources to validate the incident.

### A. Packet Capture (The Raw Truth)
We ran tcpdump on the victim host to capture every byte of traffic.

-   **Stats:** 100,511 packets captured with zero drops.
-   **Command used:**
    ```bash
    sudo tcpdump -i ens33 -w /tmp/case01-v7.pcap host 192.168.10.10
    ```

<img width="664" height="68" alt="Screenshot 2026-08-29 151514" src="https://github.com/user-attachments/assets/c947d68b-a2b3-4524-90bf-1f6ff479a11d" />


### B. Attacker Perspective (Intent Confirmation)
From the Kali side, we confirmed the specific tool and parameters used.

-   **Command used:**
    ```bash
    sudo nmap -sS -Pn -p 1-100 --min-rate 10000 --script=default 192.168.20.10
    ```
-   **Key Finding:** Port 22/tcp identified as **filtered ssh**. The firewall successfully blocked the SYN probes, preventing port state disclosure while still triggering IDS alerts due to packet volume.

<img width="850" height="90" alt="Screenshot 2026-08-29 151624" src="https://github.com/user-attachments/assets/054fac36-3ad6-468f-b49d-d0fbe84dac81" />


### C. IDS Alert Log (Real-time Detection)
Suricata logged the anomaly the moment it occurred.

> **Note:** The topmost entry in the log (Source `91.189.92.22`) is unrelated background internet noise targeting port 80. Our focus is strictly on the correlated alerts from `192.168.10.10` below it, which show repeated SYN/ACK manipulation at timestamp `01:05:20`.

-   **Source:** pfSense WebGUI > Services > Suricata > Alerts

<img width="626" height="332" alt="Screenshot 2026-08-29 151548" src="https://github.com/user-attachments/assets/da5768ed-9c96-44fe-963c-ca6c1cef485b" />


---

## 3. Reproduction Steps
Here is the exact workflow used to generate this incident. You can replicate this in your own lab environment.

### Phase 1: Preparation and Baseline
1.  **Ensure Suricata is Running:** Go to pfSense WebGUI > Services > Suricata > Interfaces. Verify OPT1 status is Running. If no alerts appear later, try restarting the service on that interface to reload rules.
2.  **Start Packet Capture on Victim:** SSH into Ubuntu (`ssh adi@192.168.20.10`). Run tcpdump targeting the attacker IP to reduce noise:
    ```bash
    sudo tcpdump -i ens33 -w /tmp/case01-v7.pcap host 192.168.10.10
    ```
    Keep this terminal open and do not press Ctrl+C yet.

### Phase 2: Executing the Attack (From Kali)
1.  **Run Nmap Scan:** Open a new terminal in Kali Linux. Execute the following command to trigger both network traffic and IDS anomalies:
    ```bash
    sudo nmap -sS -Pn -p 1-100 --min-rate 10000 --script=default 192.168.20.10
    ```
2.  **Understanding the Flags:**
    -   `-sS`: SYN Scan (Half-open). Creates incomplete handshakes that trigger Stream alerts.
    -   `-Pn`: Skip host discovery. Bypasses ICMP blocks.
    -   `--min-rate 10000`: High speed. Forces Suricata to process packets rapidly, increasing the chance of anomaly detection.
    -   `--script=default`: Adds variety to packet payloads, triggering deeper inspection.

### Phase 3: Capturing Evidence
1.  **Stop Capture:** Wait for Nmap to finish. Switch back to the Ubuntu terminal and press `Ctrl+C`. Verify the packet count matches the expected volume (e.g., 100,511 packets captured).
2.  **Check IDS Alerts:** Go to pfSense WebGUI > Services > Suricata > Alerts. Select Instance `(OPT1) OPT1` and click Refresh. Look for `SURICATA STREAM` alerts with Source `192.168.10.10`.

#### Expected Outcome
If successful, you should see over 100,000 packets captured in tcpdump, Port 22 listed as filtered in Nmap (indicating firewall intervention), and multiple SURICATA STREAM entries with SID `1:2210008` or `1:2210004` sourced from the attacker IP.

---

## 4. Context and Baseline
-   **Target:** Ubuntu Server (`192.168.20.10`) running SSH.
-   **Network Zone:** Isolated segment (OPT1 / `192.168.20.0/24`).
-   **Normal Behavior:** Legitimate SSH logins complete the full 3-way handshake smoothly. Bursty traffic with failed or resent handshakes is not expected and indicates automation.

---

## 5. Deep Dive Analysis
Here is what the evidence tells us when analyzed together.

-   **Scan Style:** The sheer volume (100k+ packets) and the SYN resend pattern show classic scanner behavior.
-   **Speed:** The `--min-rate 10000` parameter means thousands of connection attempts per second. No human interacts at this speed.
-   **Protocol Weirdness:** The `different seq` alert means the source was cycling through sequence numbers rapidly. This is a common technique for OS fingerprinting or bypassing basic stateful checks.
-   **Firewall Effectiveness:** Nmap reported port 22 as "filtered" rather than "open". This confirms the pfSense firewall successfully dropped or rejected the SYN probes, yet the traffic volume was still sufficient to trigger behavioral IDS alerts.
-   **Human vs Machine:** Manual SSH has latency and pauses. This traffic was mechanical, bursty, and relentless.

---

## 6. MITRE ATT&CK Mapping
Every SOC report needs to speak the universal language. Here is where this activity fits.

| Tactic | Technique ID | Name | Application in This Case |
| :--- | :--- | :--- | :--- |
| **Reconnaissance** | `T1046` | Network Service Scanning | Attacker scanned target to find open SSH service on port 22 using Nmap. |
| **Discovery** | `T1040` | Network Sniffing | Potential passive sniffing occurring before active scan. |
| **Initial Access** | `T1110` | Brute Force | Finding open SSH is the prerequisite for credential attacks. |

> **Tactical Insight:** We caught this in the Pre-Compromise phase. Stopping T1046 early buys time to harden systems before the attacker moves to T1110 or beyond.

---

## 7. Verdict
-   **Classification:** MALICIOUS (Active Reconnaissance)

This is textbook Kill Chain Stage 1. No data was stolen and no shell was gained, but the intent is clear. Identifying open services is how attackers plan their next move. Catching it here is a defensive win.

---

## 8. Recommended Actions
What should happen next in a real SOC queue.

1.  **Immediate Block:** Drop IP `192.168.10.10` at pfSense firewall (OPT1 inbound).
2.  **Host Hardening:** Deploy Fail2Ban on Ubuntu to auto-ban IPs after 3-5 rapid connection attempts to port 22.
3.  **Detection Tuning:** Add custom Suricata or Wazuh rules for high-rate SYN bursts to sensitive ports.
4.  **Log Review:** Check `/var/log/auth.log` on Ubuntu to ensure no successful logins slipped through during the scan window.

---

## Detection Ruleset & Configuration
The detection was powered by the **Emerging Threats Open Rules** suite, updated on Aug-29 2026.

<img width="655" height="251" alt="Screenshot 2026-08-29 153352" src="https://github.com/user-attachments/assets/d021c63a-283c-4599-9d11-993a4fccb168" />


> **Note on Signature vs. Behavioral Detection:**
> Although the ETOpen ruleset was active and updated, the primary alerts triggered (`SID 1:2210008`, `1:2210004`) were **Suricata Stream Engine anomalies**, not specific ET signatures like "ET SCAN Nmap".
>
> This happened because modern scanners (like Nmap with `-sS`) often mimic legitimate traffic patterns closely enough to bypass static signatures. However, they cannot fake the TCP handshake physics. The Suricata stream tracker detected the *impossible* sequence number resends and incomplete handshakes, proving that **behavioral analysis is often superior to signature matching** for detecting evasive reconnaissance.

---

> **Notes for Future Reference:** This case proves that behavioral detection (stream anomalies) often catches modern scanners better than static signatures. Always triangulate using network alerts, packet captures, and attacker logs to build a solid incident narrative. The next step, Case-02, will simulate what happens if the attacker actually tries to brute force the SSH port we just found open.
