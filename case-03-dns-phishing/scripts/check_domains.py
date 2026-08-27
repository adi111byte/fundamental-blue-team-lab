"""
Extract domains found in an .eml file and check their reputation using
the VirusTotal public API.

Usage:
    export VT_API_KEY=your_key_here
    python check_domains.py path/to/sample.eml

Notes:
- Get a free API key at virustotal.com (public API has a request rate limit,
  this script does not implement retry/backoff, add it if scanning many domains).
- This script only reads the .eml file locally, it does not open any link.
"""

import argparse
import os
import re
import sys
import time
import urllib.request
import json

DOMAIN_PATTERN = re.compile(r"https?://([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})")


def extract_domains(eml_path):
    with open(eml_path, "r", errors="ignore") as f:
        content = f.read()
    domains = sorted(set(DOMAIN_PATTERN.findall(content)))
    return domains


def check_domain_reputation(domain, api_key):
    url = f"https://www.virustotal.com/api/v3/domains/{domain}"
    req = urllib.request.Request(url, headers={"x-apikey": api_key})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            stats = data["data"]["attributes"]["last_analysis_stats"]
            return stats
    except Exception as e:
        return {"error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="Extract and check domain reputation from an .eml file")
    parser.add_argument("emlfile", help="Path to the .eml sample")
    args = parser.parse_args()

    api_key = os.environ.get("VT_API_KEY")
    if not api_key:
        print("Set VT_API_KEY environment variable first.")
        sys.exit(1)

    domains = extract_domains(args.emlfile)
    if not domains:
        print("No domains found in this file.")
        return

    print(f"Found {len(domains)} unique domain(s):\n")
    for domain in domains:
        stats = check_domain_reputation(domain, api_key)
        print(f"  {domain}: {stats}")
        time.sleep(15)  # free tier rate limit, adjust if needed


if __name__ == "__main__":
    main()
