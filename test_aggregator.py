#!/usr/bin/env python3
"""
Automated verification test suite for Whitelist Proxy Aggregator.
Verifies all Acceptance Criteria from R1-R4.
"""

import os
import yaml
import unittest

class TestWhitelistAggregator(unittest.TestCase):
    def setUp(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.clash_file = os.path.join(self.base_dir, "clash.yaml")
        self.workflow_file = os.path.join(self.base_dir, ".github", "workflows", "update.yml")
        self.readme_file = os.path.join(self.base_dir, "README.md")
        
        self.assertTrue(os.path.exists(self.clash_file), "clash.yaml must exist")
        with open(self.clash_file, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)

    def test_clash_yaml_is_valid_dict(self):
        self.assertIsInstance(self.config, dict)
        self.assertIn("proxies", self.config)
        self.assertIn("proxy-groups", self.config)
        self.assertIn("rules", self.config)

    def test_proxy_count_within_bounds(self):
        proxies = self.config.get("proxies", [])
        self.assertGreaterEqual(len(proxies), 250, "Proxy count must be at least 250")
        self.assertLessEqual(len(proxies), 300, "Proxy count must not exceed 300")
        print(f"[TEST PASS] Proxy count verified: {len(proxies)} (within 250-300 bounds)")

    def test_proxy_endpoints_are_unique(self):
        proxies = self.config.get("proxies", [])
        seen_signatures = set()
        seen_names = set()
        for p in proxies:
            path = p.get('ws-opts', {}).get('path', '') if isinstance(p.get('ws-opts'), dict) else ''
            sig = f"{p['type']}:{p['server']}:{p['port']}:{p.get('uuid') or p.get('password')}:{p.get('client-fingerprint', '')}:{p.get('servername', '')}:{path}"
            self.assertNotIn(sig, seen_signatures, f"Duplicate proxy configuration detected: {sig}")
            seen_signatures.add(sig)
            self.assertNotIn(p["name"], seen_names, f"Duplicate proxy name: {p['name']}")
            seen_names.add(p["name"])
        print(f"[TEST PASS] All {len(seen_names)} proxy names and configurations are strictly unique")

    def test_proxy_groups_structure(self):
        groups = {g["name"]: g for g in self.config.get("proxy-groups", [])}
        self.assertIn("🚀 VIP-Auto-Select", groups)
        self.assertIn("🛡️ Emergency-Fallback", groups)
        self.assertIn("🇷🇺 Russian-Reserve", groups)
        self.assertIn("🌐 Manual-Select", groups)
        self.assertIn("GLOBAL", groups)
        
        vip_group = groups["🚀 VIP-Auto-Select"]
        self.assertEqual(vip_group["type"], "url-test")
        self.assertTrue("pitbit.com" in vip_group["url"] or "1.1.1.1" in vip_group["url"] or "trustpool" in vip_group["url"])
        
        fallback_group = groups["🛡️ Emergency-Fallback"]
        self.assertEqual(fallback_group["type"], "fallback")
        self.assertIn("🚀 VIP-Auto-Select", fallback_group["proxies"])
        self.assertIn("🇷🇺 Russian-Reserve", fallback_group["proxies"])
        print("[TEST PASS] Proxy groups verified with correct url-test and fallback failover")

    def test_routing_and_bypass_rules(self):
        rules = self.config.get("rules", [])
        self.assertTrue(any("trustpool" in r and "VIP-Auto-Select" in r for r in rules), "Trustpool proxy rule missing")
        self.assertTrue(any("stratum" in r and "VIP-Auto-Select" in r for r in rules), "Stratum proxy rule missing")
        self.assertTrue(any("3333" in r and "VIP-Auto-Select" in r for r in rules), "Stratum port 3333 proxy rule missing")
        self.assertTrue(any("pitbit" in r and "VIP-Auto-Select" in r for r in rules), "Pitbit firmware proxy rule missing")
        self.assertTrue(any("jsdelivr" in r and "VIP-Auto-Select" in r for r in rules), "Self-update jsdelivr proxy rule missing")
        self.assertTrue(any("github" in r and "VIP-Auto-Select" in r for r in rules), "Self-update github proxy rule missing")
        self.assertTrue(any("GEOIP,RU,DIRECT" in r for r in rules), "Russian domestic bypass rule missing")
        self.assertTrue(rules[-1].startswith("MATCH,"), "Last rule must be MATCH")
        print("[TEST PASS] Custom routing rules and Russian bypass rules verified")

    def test_github_workflow_validity(self):
        self.assertTrue(os.path.exists(self.workflow_file), "GitHub Actions workflow must exist")
        with open(self.workflow_file, "r", encoding="utf-8") as f:
            wf = yaml.safe_load(f)
        trigger_section = wf.get("on") or wf.get(True)
        self.assertIsNotNone(trigger_section, "Trigger section must exist in workflow")
        self.assertIn("schedule", trigger_section)
        cron_expr = trigger_section["schedule"][0]["cron"]
        self.assertEqual(cron_expr, "0 */2 * * *", "Cron schedule must be every 2 hours")
        print("[TEST PASS] GitHub Actions workflow syntax and 2-hour cron schedule verified")

if __name__ == "__main__":
    unittest.main()
