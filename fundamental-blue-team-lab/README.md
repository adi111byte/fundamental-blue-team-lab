# Blue Team Triage Lab

A set of self contained incident triage cases built in a home lab with pfSense as the network boundary. Each case documents a specific attack scenario from detection to writeup, including detection rules and small scripts used along the way.

Bahasa Indonesia summary: see [README_id.md](./README_id.md)

## Why this repo exists

I wanted a portfolio that shows how I actually triage an incident, not just a list of tools I installed. Every case follows the same process (see `docs/triage-sop.md`) so the reasoning stays consistent across different attack types.

## Lab setup

pfSense runs as the router/firewall between an attacker VM and one or more target VMs in VirtualBox. Full topology and reproduction steps are in `docs/lab-setup.md`.

## Cases

| Case | Attack type | Detection method | Status |
|---|---|---|---|
| [case-01-port-scan](./case-01-port-scan) | Nmap port scan | Suricata (pfSense) | In progress |
| [case-02-ssh-bruteforce](./case-02-ssh-bruteforce) | SSH brute force | auth.log + custom Python parser | In progress |
| [case-03-dns-phishing](./case-03-dns-phishing) | Phishing domains | Manual header review + domain reputation script | In progress |

## Shared docs

- `docs/triage-sop.md`: the 6 step process used in every case
- `docs/lab-setup.md`: how to reproduce the lab
- `docs/wireshark-filters.md`: filters actually used across cases, not a generic cheat sheet

## Final report

`report/final-report.md` summarizes all three cases in one place for a quick read.

## Contact

adirmadhani@gmail.com | [LinkedIn](https://www.linkedin.com/in/adiramadhani-148400353)
