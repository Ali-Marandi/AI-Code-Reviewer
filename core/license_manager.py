import hashlib

class LicenseManager:
    def __init__(self, license_key=None):
        self.license_key = license_key
        self.is_active = False
        if license_key:
            self.validate_key(license_key)

    def validate_key(self, key):
        if not key or not key.startswith("AI-ENT-"):
            self.is_active = False
            return False
        self.is_active = True
        return True

    def get_status(self):
        return "Active (Enterprise)" if self.is_active else "Inactive / Community Edition"

    def get_features_enabled(self):
        if self.is_active:
            return ["Deep Logic Review", "SAST Scanning", "Priority AI Queue", "Team Analytics"]
        return ["Basic Code Review"]
