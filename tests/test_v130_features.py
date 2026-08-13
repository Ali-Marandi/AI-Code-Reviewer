import unittest
from core.ai_engine_v130_features import EnterpriseAdvancedAnalyticsEngine

class TestEnterprisev130Features(unittest.TestCase):
    def setUp(self):
        self.engine = EnterpriseAdvancedAnalyticsEngine()

    def test_technical_debt_calculation(self):
        findings = [
            {"severity": "High", "rule_id": "ACR-LOCAL-GITHUB-TOKEN"},
            {"severity": "Medium", "rule_id": "CUSTOM-1"},
            {"severity": "Low", "rule_id": "CUSTOM-2"}
        ]
        result = self.engine.calculate_technical_debt_score(findings, 5000)
        self.assertIn("debt_density_per_k_loc", result)
        self.assertIn("code_quality_grade", result)
        self.assertEqual(result["codebase_loc"], 5000)

    def test_cross_repo_policy_synthesis(self):
        profiles = [
            {"repo": "backend-api", "grade": "A"},
            {"repo": "frontend-app", "grade": "B"},
            {"repo": "legacy-service", "grade": "D"}
        ]
        synthesis = self.engine.synthesize_cross_repo_policy(profiles)
        self.assertEqual(synthesis["total_repositories_analyzed"], 3)
        self.assertEqual(synthesis["compliant_repositories"], 2)
        self.assertTrue(synthesis["action_required"])

if __name__ == "__main__":
    unittest.main()
