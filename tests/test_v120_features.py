import unittest
from core.ai_engine_v120_features import EnterpriseExtensionEngine

class TestEnterprisev120Features(unittest.TestCase):
    def setUp(self):
        self.engine = EnterpriseExtensionEngine("rules/policy_exemptions.json")

    def test_policy_exemption_matching(self):
        # Test that exemptions in test files are correctly recognized
        self.assertTrue(self.engine.is_exempted("ACR-LOCAL-API-KEY", "tests/test_foo.py", 10))
        self.assertFalse(self.engine.is_exempted("ACR-LOCAL-API-KEY", "src/main.py", 10))

    def test_refactoring_patch_generation(self):
        original = "    api_key = \"sk-proj-fake-secret-token-123456789\"\n    print(api_key)\n"
        patch = self.engine.generate_refactoring_patch(original, "ACR-LOCAL-OPENAI-KEY", 1)
        self.assertIsNotNone(patch)
        self.assertIn("os.environ.get", patch)

if __name__ == "__main__":
    unittest.main()
