# Triage SOP

This is the process I follow for every case in this repo. Writing it down once here keeps each case README focused on findings instead of repeating the same explanation.

## 1. Identify the trigger
What alert, log entry, or observation started the investigation. Record the timestamp and source.

## 2. Gather evidence
Collect the relevant logs, pcap, or files. Keep raw evidence in each case's `evidence/` folder. Never modify the original file, work on a copy if parsing or filtering is needed.

## 3. Establish context
Which host, which user, which time window. Check what is normal for that host/user before deciding something is abnormal.

## 4. Analyze
Look for the specific indicators relevant to that attack type (failed logins, scan patterns, header mismatches, etc). Document what was checked, not just the conclusion.

## 5. Determine verdict
State clearly: malicious, suspicious, or benign, and why. If a detection rule was written for this case, link it here.

## 6. Recommend action
What would happen next in a real environment: block, escalate, monitor, or close as false positive.

Each case README follows these six sections in order.
