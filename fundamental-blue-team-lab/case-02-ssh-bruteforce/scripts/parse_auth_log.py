"""
Parse an auth.log file and flag source IPs with more failed SSH logins
than the given threshold within a given time window.

Usage:
    python parse_auth_log.py path/to/auth.log --threshold 10 --window 5

This is a starting point, not a finished tool. Adjust the regex if your
auth.log format differs, and add real timestamps handling if you want
the time window check to be exact rather than a simple total count.
"""

import argparse
import re
from collections import defaultdict

FAILED_LOGIN_PATTERN = re.compile(
    r"Failed password for (?:invalid user )?(?P<user>\S+) from (?P<ip>\d+\.\d+\.\d+\.\d+)"
)


def parse_log(path):
    attempts_by_ip = defaultdict(list)
    with open(path, "r", errors="ignore") as f:
        for line in f:
            match = FAILED_LOGIN_PATTERN.search(line)
            if match:
                ip = match.group("ip")
                user = match.group("user")
                attempts_by_ip[ip].append(user)
    return attempts_by_ip


def main():
    parser = argparse.ArgumentParser(description="Flag brute force patterns in auth.log")
    parser.add_argument("logfile", help="Path to auth.log")
    parser.add_argument("--threshold", type=int, default=10, help="Minimum failed attempts to flag an IP")
    args = parser.parse_args()

    attempts_by_ip = parse_log(args.logfile)

    print(f"Parsed {sum(len(v) for v in attempts_by_ip.values())} failed login lines "
          f"from {len(attempts_by_ip)} unique source IPs.\n")

    flagged = {ip: users for ip, users in attempts_by_ip.items() if len(users) >= args.threshold}

    if not flagged:
        print("No source IP exceeded the threshold.")
        return

    print(f"IPs with >= {args.threshold} failed attempts:\n")
    for ip, users in sorted(flagged.items(), key=lambda x: -len(x[1])):
        unique_users = set(users)
        print(f"  {ip}: {len(users)} attempts, {len(unique_users)} unique usernames tried")


if __name__ == "__main__":
    main()
