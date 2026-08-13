import unittest
from core.ai_engine_v140_features import EnterpriseExploitabilityEngine

class TestEnterprisev140Features(unittest.TestCase):
    def setUp(self):
        self.engine = EnterpriseExploitabilityEngine()

    def test_exploitability_analysis_positive(self):
        # Test when vulnerable symbol is actively invoked
        result = self.engine.analyze_dependency_exploitability("requests", "2.28.0", ["requests.packages.urllib3"])
        self.assertTrue(result["is_exploitable_in_context"])
        self.assertEqual(result["severity"], "High")

    def test_exploitability_analysis_negative(self):
        # Test when vulnerable symbol is NOT invoked (false positive reduction)
        result = self.engine.analyze_dependency_exploitability("requests", "2.28.0", ["safe_get_method"])
        self.assertFalse(result["is_exploitable_in_context"])
        self.assertIn("Low priority", result["recommended_action"])

if __name__ == "__main__":
    unittest.main()
