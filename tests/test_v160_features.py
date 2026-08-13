import unittest
from core.ai_engine_v160_features import EnterpriseSBOMRemediationEngine

class TestEnterprisev160Features(unittest.TestCase):
    def setUp(self):
        self.engine = EnterpriseSBOMRemediationEngine()

    def test_sbom_generation_and_remediation(self):
        deps = [
            {"name": "lodash", "version": "4.17.20", "is_vulnerable": True, "fixed_version": "4.17.21", "ecosystem": "npm"},
            {"name": "express", "version": "4.18.1", "is_vulnerable": False, "ecosystem": "npm"}
        ]
        result = self.engine.generate_and_remediate_sbom(deps)
        self.assertEqual(result["total_components_cataloged"], 2)
        self.assertEqual(result["vulnerabilities_detected"], 1)
        self.assertEqual(result["automated_remediation_plan"][0]["component"], "lodash")

if __name__ == "__main__":
    unittest.main()
