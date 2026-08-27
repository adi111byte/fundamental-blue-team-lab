# Wireshark Filters Used in This Lab

Filters actually used while working through the cases in this repo, kept here so they are not repeated in every case README. Add to this list only after actually using a filter in a case, not as a generic reference copy.

## Port scan detection (case-01)

```
tcp.flags.syn == 1 and tcp.flags.ack == 0
```
Isolates SYN only packets, useful for spotting a scan pattern (many destination ports, same source, short interval).

## Filtering by host

```
ip.addr == <target-ip>
```
Narrow the capture down to traffic involving one host before digging further.

## Notes

This file will grow as more cases are added. Each entry should say what it is for, not just the raw filter syntax.
