# Lab Setup — Case 02: SSH Brute Force (Wazuh)

Same base topology as case-01, with a Wazuh manager added on the LAN segment. The Ubuntu target runs a Wazuh agent that forwards auth events across pfSense to the manager, so the brute force attempt is detected through Wazuh instead of read manually from `auth.log`.

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
                        └───────┬──────────────────┬────────┘
                                │                  │
                LAN segment     │                  │   OPT1 segment
                192.168.10.0/24 │                  │   192.168.20.0/24
                                │                  │
        ┌───────────────────────┴──┐              └──┬────────────────────────┐
        │                          │                 │                        │
┌───────┴────────┐      ┌──────────┴───────┐         │            ┌────────────┴──────── ┐
│ Kali (attacker) │      │ Wazuh Manager    │         │           │ Ubuntu 22.04 (target)│
│ 192.168.10.10   │      │ 192.168.10.20    │◄────────┴───────────┤ 192.168.20.10        │
│ gw: 192.168.10.1│      │ manager+indexer  │  1514/tcp, 1515/tcp │ gw: 192.168.20.1      │
│ hydra           │      │ +dashboard       │                     │ Wazuh Agent, OpenSSH  │
└─────────────────┘      └──────────────────┘                     └───────────────────────┘
```

### Why this topology

The Wazuh manager sits on the LAN segment, separate from the target it monitors. The agent on Ubuntu (OPT1) has to reach the manager across pfSense, so the same OPT1-has-no-default-rule issue from case-01 applies again here, this time for the agent's outbound connection instead of an attacker's inbound one.

## Components

| Component | Detail |
|---|---|
| Hypervisor | VMware Workstation |
| Router/Firewall | pfSense CE |
| Attacker VM | Kali Linux — `192.168.10.10/24` |
| Target VM | Ubuntu Server 22.04 — `192.168.20.10/24`, Wazuh agent installed |
| Wazuh Manager | `192.168.10.20/24` (LAN segment), all-in-one install (manager + indexer + dashboard) |

## pfSense configuration checklist

- [x] Base OPT1 allow rule from case-01 already in place
- [ ] Additional OPT1 rule: allow Ubuntu (`192.168.20.10`) → Wazuh Manager (`192.168.10.20`) on ports `1514/tcp` and `1515/tcp` (agent event forwarding and registration)
- [ ] Wazuh manager reachable from Ubuntu — verify before registering the agent

## Verifying the agent can reach the manager

```bash
# on Ubuntu (target)
ping 192.168.10.20
nc -zv 192.168.10.20 1514
nc -zv 192.168.10.20 1515
```

If either port fails, the agent will show as "never connected" in the Wazuh dashboard — check the OPT1 firewall rule above before troubleshooting the agent config itself.

## Registering the agent

```bash
# on Ubuntu (target), after installing wazuh-agent
/var/ossec/bin/agent-auth -m 192.168.10.20
```

Set `<address>192.168.10.20</address>` under `<client><server>` in `/var/ossec/etc/ossec.conf`, then:

```bash
systemctl restart wazuh-agent
/var/ossec/bin/wazuh-control status
```

Confirm the agent shows "Active" on the manager's Agents page before running the brute force attempt.

## Safety

- Kali, Ubuntu, and the Wazuh manager only exist on their respective host-only segments; the only path to the internet is pfSense's WAN.
- The brute force attempt is never pointed outside `192.168.10.0/24` / `192.168.20.0/24`.
- VM snapshot reverted after the session, wordlist used is lab-only and never reused elsewhere.
