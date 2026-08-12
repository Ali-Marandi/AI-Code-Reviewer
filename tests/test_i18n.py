import unittest

from core.i18n import DEFAULT_LOCALE, SUPPORTED_LOCALES, normalize_locale


class LocalizationTests(unittest.TestCase):
    def test_supported_locale_is_preserved(self):
        self.assertEqual(normalize_locale("fa"), "fa")
        self.assertEqual(normalize_locale("en_US"), "en")

    def test_unsupported_locale_falls_back_to_default(self):
        self.assertEqual(normalize_locale("de-DE"), DEFAULT_LOCALE)
        self.assertEqual(normalize_locale("../../untrusted"), DEFAULT_LOCALE)

    def test_supported_locale_set_is_explicit_and_small(self):
        self.assertEqual(SUPPORTED_LOCALES, {"en", "fa"})


if __name__ == "__main__":
    unittest.main()
