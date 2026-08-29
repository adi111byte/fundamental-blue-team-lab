# Lab Setup - Case 01: Port Scan Detection

Isolated VMware lab with pfSense as router/firewall between two host-only segments. Traffic from the attacker to the target passes through pfSense, which is what makes the Suricata alert (or lack of one) in this case meaningful.

## Topology

```text
                        ┌──────────────────────────────────┐
                        │              Internet            │
                        │   (package/rule updates only)    │
                        └────────────────┬─────────────────┘
                                          │ WAN
                        ┌─────────────────┴─────────────────┐
                        │               pfSense             │
                        │  LAN  (em1): 192.168.10.1/24      │
                        │  OPT1 (em2): 192.168.20.1/24      │
                        │  Suricata enabled on OPT1         │
                        └───────┬──────────────────┬────────┘
                                │                  │
                LAN segment     │                  │   OPT1 segment
                192.168.10.0/24 │                  │   192.168.20.0/24
                                │                  │
        ┌────────────────────────────┐   ┌────────────────────────────┐
        │  Kali (attacker)           │   │  Ubuntu 22.04 (target)     │
        │  192.168.10.10/24          │   │  192.168.20.10/24          │
        │  gw: 192.168.10.1          │   │  gw: 192.168.20.1          │
        │  nmap, tcpdump             │   │  tcpdump                   │
        └────────────────────────────┘   └────────────────────────────┘
```

### Why this topology

Kali and Ubuntu sit on two different host-only segments instead of sharing one subnet. If they shared a subnet, the scan traffic would go directly VM-to-VM and Suricata on pfSense's OPT1 interface would never see it. Routing through separate segments forces every packet through pfSense, where Suricata can inspect it.

## Components

| Component | Detail |
|---|---|
| Hypervisor | VMware Workstation |
| Router/Firewall | pfSense CE, Suricata package on OPT1 |
| Attacker VM | Kali Linux — `192.168.10.10/24` |
| Target VM | Ubuntu Server 22.04 — `192.168.20.10/24` |
| LAN interface | `em1` — `192.168.10.1/24` |
| OPT1 interface | `em2` — `192.168.20.1/24` |

## pfSense configuration checklist

OPT1 has no default firewall rule (unlike LAN, which allows any-to-any out of the box). Without an explicit allow rule, the target is unreachable before any traffic can even be tested.

- [x] LAN and OPT1 interfaces enabled with the addressing above
- [x] Firewall rule added on OPT1: pass, source `OPT1 net`, destination any
- [x] Suricata installed, assigned to OPT1, interface status green
- [ ] Suricata rule categories enabled under Categories tab (`emerging-scan.rules`) — verify before relying on alert output
- [x] Connectivity confirmed: Kali can reach Ubuntu through pfSense

## Verifying traffic actually routes through pfSense

```bash
# from Kali
ping 192.168.20.10
traceroute 192.168.20.10   # expect: 192.168.10.1 -> 192.168.20.10
```

If the traceroute shows only one hop, the two VMs are on the same broadcast domain and Suricata will not see anything — check the VMware network adapter assignment before running the scan.

## Safety

- Kali and Ubuntu only exist on their host-only segments; the only path to the internet is pfSense's WAN, used solely for Suricata rule updates.
- Traffic is never pointed outside `192.168.10.0/24` / `192.168.20.0/24`.
- VM snapshot reverted after the session.
