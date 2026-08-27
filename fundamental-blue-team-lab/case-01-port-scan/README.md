# Case 01: Port Scan Detection

Status: in progress, template only

## 1. Identify the trigger
(To fill in: Suricata alert on pfSense, timestamp, source IP)

## 2. Gather evidence
(To fill in: screenshot of Suricata alert, pcap if captured, saved in `evidence/`)

## 3. Establish context
(To fill in: which host was scanned, was this expected traffic or not)

## 4. Analyze
(To fill in: which ports were probed, scan type, how fast, does it match a known scan technique like SYN scan)

## 5. Verdict
(To fill in: malicious/suspicious/benign, reasoning)

## 6. Recommended action
(To fill in: what would happen next in a real SOC)

## Detection rule

See `detection/suricata-port-scan.rules` for the rule used or reviewed for this case.

## Files

- `evidence/`: screenshots and/or pcap from this case
- `detection/`: Suricata rule related to this detection
