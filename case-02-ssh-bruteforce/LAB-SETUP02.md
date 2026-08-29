# Lab Setup — Case 02: SSH Brute Force (Wazuh)

Isolated VMware lab with pfSense as router/firewall between two host-only segments, extended from case-01 with a Wazuh manager on the LAN segment. The Ubuntu target runs a Wazuh agent that forwards authentication events across pfSense to the manager, so the brute force attempt is detected through Wazuh's correlation engine instead of read manually from `auth.log`.

## Topology

```text
                        ┌──────────────────────────────────┐
                        │              Internet             │
                        │   (package/rule updates only)     │
                        └────────────────┬───────────────────┘
                                          │ WAN - VMnet8 (NAT)
                        ┌─────────────────┴─────────────────┐
                        │               pfSense              │
                        │  LAN  (em1): 192.168.10.1/24       │
                        │  OPT1 (em2): 192.168.20.1/24       │
                        └───────┬──────────────────┬─────────┘
                                │                  │
                 LAN (VMnet2)   │                  │   OPT1 (VMnet3)
              192.168.10.0/24   │                  │   192.168.20.0/24
                                │                  │
        ┌───────────────────────┴──┐              └──┬────────────────────────┐
        │                          │                 │                        │
┌───────┴────────┐      ┌──────────┴───────┐         │           ┌────────────┴────────┐
│ Kali (attacker) │      │ Wazuh Manager    │         │           │ Ubuntu 22.04 (target)│
│ 192.168.10.10   │      │ 192.168.10.20    │◄────────┴───────────┤ 192.168.20.10        │
│ gw: 192.168.10.1│      │ manager+indexer  │  1514/tcp, 1515/tcp │ gw: 192.168.20.1      │
│ hydra           │      │ +dashboard       │  (through pfSense)  │ Wazuh Agent, OpenSSH  │
└─────────────────┘      └──────────────────┘                     └───────────────────────┘
```

### Why this topology

The Wazuh manager sits on the LAN segment, separate from the target subnet it monitors. The agent on Ubuntu (OPT1) has to reach the manager across pfSense, so the same OPT1-has-no-default-rule issue from case-01 applies again here, this time for the agent's outbound connection rather than an attacker's inbound scan. This mirrors how a real SIEM deployment usually sits on a separate management segment from the hosts it watches.

## Components

| Component | Detail |
|---|---|
| Hypervisor | VMware Workstation |
| Router/Firewall | pfSense CE |
| Attacker VM | Kali Linux — `192.168.10.10/24` |
| Target VM | Ubuntu Server 22.04 — `192.168.20.10/24`, Wazuh agent + OpenSSH |
| Wazuh Manager | `192.168.10.20/24` (LAN segment), all-in-one install (manager + indexer + dashboard) |
| Networks | VMnet8 (NAT), VMnet2 (LAN, host-only), VMnet3 (OPT1, host-only) |

DNS for all VMs: their respective pfSense interface IP (pfSense DNS forwarder).

## Addressing

| Device | NIC | VMware network | IP | Gateway |
|---|---|---|---|---|
| pfSense | WAN | VMnet8 (NAT) | DHCP | VMware NAT gateway |
| pfSense | LAN | VMnet2 | 192.168.10.1/24 | — |
| pfSense | OPT1 | VMnet3 | 192.168.20.1/24 | — |
| Kali | eth0 | VMnet2 | 192.168.10.10/24 | 192.168.10.1 |
| Wazuh Manager | eth0 | VMnet2 | 192.168.10.20/24 | 192.168.10.1 |
| Ubuntu | eth0 | VMnet3 | 192.168.20.10/24 | 192.168.20.1 |

## VM NIC assignment

| VM | NIC 1 |
|---|---|
| Kali | VMnet2 |
| Wazuh Manager | VMnet2 |
| Ubuntu | VMnet3 |

(pfSense keeps its 3-NIC assignment from case-01: WAN/LAN/OPT1 on VMnet8/VMnet2/VMnet3.)

## pfSense configuration checklist

OPT1 has no default firewall rule (unlike LAN, which allows any-to-any out of the box). Without the additional rule below, the Wazuh agent on Ubuntu can never reach the manager, and it will sit at "never connected" indefinitely with no obvious error.

- [x] Base OPT1 allow rule from case-01 already in place (source `OPT1 net`, destination any)
- [ ] Additional OPT1 rule: **Pass**, source `192.168.20.10` (or `OPT1 net` if reused later), destination `192.168.10.20`, ports `1514/tcp` and `1515/tcp`
- [ ] Apply Changes clicked after adding the rule
- [ ] Wazuh manager installed and dashboard reachable at `https://192.168.10.20` from the LAN segment

## Installing Wazuh (all-in-one) on the manager VM

```bash
curl -sO https://packages.wazuh.com/4.7/wazuh-install.sh
sudo bash ./wazuh-install.sh -a
```

This installs the manager, indexer, and dashboard together. Note the admin credentials printed at the end of the script — they are needed to log into `https://192.168.10.20`.

## Verifying the agent can reach the manager

Run this from Ubuntu **before** installing the agent, to confirm the network path is open first:

```bash
ping 192.168.10.20
nc -zv 192.168.10.20 1514
nc -zv 192.168.10.20 1515
```

If either `nc` command fails, the OPT1 firewall rule above is the first thing to check — don't move on to agent troubleshooting until this passes.

## Installing and registering the agent

```bash
# on Ubuntu (target)
curl -o wazuh-agent.deb https://packages.wazuh.com/4.x/apt/pool/main/w/wazuh-agent/wazuh-agent_4.7.0-1_amd64.deb
WAZUH_MANAGER='192.168.10.20' dpkg -i ./wazuh-agent.deb

/var/ossec/bin/agent-auth -m 192.168.10.20
```

Confirm `<address>192.168.10.20</address>` is set under `<client><server>` in `/var/ossec/etc/ossec.conf`, then:

```bash
systemctl daemon-reload
systemctl enable wazuh-agent
systemctl restart wazuh-agent
/var/ossec/bin/wazuh-control status
```

On the manager dashboard (Agents page), the Ubuntu host should show status **Active**. Do not proceed to the brute force attempt until this is confirmed — an agent that looks "Active" but was registered before the firewall rule was added can silently fail to forward events.

## Verifying event flow before the actual attack

Trigger one intentional failed login from Kali as a smoke test:

```bash
ssh invaliduser@192.168.20.10
```

Check the Wazuh dashboard's Security Events view for a corresponding authentication failure event within a minute or two. If nothing appears, recheck ports 1514/1515 and the agent status before running the real brute force in case-02's README.

## Safety

- Kali, Ubuntu, and the Wazuh manager only exist on their respective host-only segments; the only path to the internet is pfSense's WAN, used solely for package updates.
- The brute force attempt is never pointed outside `192.168.10.0/24` / `192.168.20.0/24`.
- VM snapshots are reverted after the session. The wordlist used is lab-only and never reused elsewhere. Wazuh dashboard admin credentials are not committed to this repo.
