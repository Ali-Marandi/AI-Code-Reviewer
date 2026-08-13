import unittest
from core.ai_engine_v150_features import EnterpriseComplianceMapperEngine

class TestEnterprisev150Features(unittest.TestCase):
    def setUp(self):
        self.engine = EnterpriseComplianceMapperEngine()

    def test_compliance_auto_mapping(self):
        findings = [
            {"rule_id": "ACR-LOCAL-GITHUB-TOKEN", "severity": "High", "description": "Hardcoded GitHub Token detected"},
            {"rule_id": "eval_injection", "severity": "Critical", "description": "Unsafe eval usage"}
        ]
        report = self.engine.map_findings_to_compliance_controls(findings)
        self.assertEqual(report["total_findings_mapped"], 2)
        self.assertIn("soc2", report["framework_violation_summary"])
        self.assertEqual(report["compliance_status"], "Action Required")

if __name__ == "__main__":
    unittest.main()
