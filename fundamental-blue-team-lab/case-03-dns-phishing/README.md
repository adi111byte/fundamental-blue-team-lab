# Case 03: DNS / Phishing Domain Review

Status: in progress, template only

## 1. Identify the trigger
(To fill in: which email sample from the dataset, why it was picked)

## 2. Gather evidence
(To fill in: header excerpt saved in `evidence/`, list of domains found in `domains.txt`)

## 3. Establish context
(To fill in: what the email claims to be, who it is impersonating if anyone)

## 4. Analyze
(To fill in: From/Reply-To/Return-Path comparison, SPF/DKIM/DMARC results, domain reputation results from the script)

## 5. Verdict
(To fill in: malicious/suspicious/benign, reasoning)

## 6. Recommended action
(To fill in: block sender domain, report, no action needed)

## Script

`scripts/check_domains.py` extracts domains from an email file and checks their reputation using a free API (e.g. VirusTotal public API). Requires an API key, see comments in the script.

## Files

- `evidence/03-domains.txt`: list of domains extracted from the sample and any screenshots
- `scripts/`: the domain check script
