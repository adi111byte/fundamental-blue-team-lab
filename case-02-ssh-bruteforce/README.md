# Case 02: SSH Brute Force

Status: in progress, template only

## 1. Identify the trigger
(To fill in: how the brute force attempt was noticed, e.g. repeated failed logins in auth.log)

## 2. Gather evidence
(To fill in: auth.log excerpt saved in `evidence/`, screenshot of terminal output)

## 3. Establish context
(To fill in: which account was targeted, is SSH normally exposed to this segment)

## 4. Analyze
(To fill in: number of attempts, time window, source IP, usernames tried)

## 5. Verdict
(To fill in: malicious/suspicious/benign, reasoning)

## 6. Recommended action
(To fill in: e.g. fail2ban, IP block, account lockout policy review)

## Detection

See `detection/sigma-ssh-bruteforce.yml` for the Sigma rule used or reviewed.

## Script

`scripts/parse_auth_log.py` parses `auth.log` and flags any source IP with more than a configurable number of failed logins within a time window.

## Files

- `evidence/`: auth.log excerpt and screenshots
- `detection/`: Sigma rule for this case
- `scripts/`: the parser script
