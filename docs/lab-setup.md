# Lab Setup

## Topology

```
[Attacker VM] --\
                  [pfSense] -- [Target VM(s)]
[Host machine] --/
```

pfSense sits between the attacker VM and the target VM(s), acting as the router and firewall. All traffic between VMs passes through it, which is what makes the Suricata alerts in case-01 possible.

## Components

- Hypervisor: VirtualBox
- Firewall/Router: pfSense (existing install)
- Attacker VM: Kali Linux
- Target VM: Ubuntu Server 22.04
- Network mode: Internal Network (all VMs on the same internal segment, no exposure to the host's real network)

## Reproduction steps

1. Create an Internal Network in VirtualBox (same name across all VM network adapters).
2. Set pfSense's WAN/LAN interfaces to bridge that internal network to the target/attacker segment.
3. Assign static IPs to attacker and target VMs within the pfSense managed subnet.
4. Confirm connectivity: attacker VM can reach target VM through pfSense (ping test).
5. Enable Suricata package on pfSense, assigned to the interface facing the target VM.

## Notes

This lab is fully isolated. No traffic leaves the internal network, and no real external targets are involved in any simulation.
