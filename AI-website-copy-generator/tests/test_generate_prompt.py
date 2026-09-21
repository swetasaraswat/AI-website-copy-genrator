import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import generate_prompt as gp  # noqa: E402


class PromptTests(unittest.TestCase):
    def test_every_business_fills_every_template(self):
        for business in gp.list_names(gp.BUSINESSES_DIR, ".json"):
            for template in gp.list_names(gp.PROMPTS_DIR, ".md"):
                with self.subTest(business=business, template=template):
                    prompt = gp.build_prompt(gp.load_business(business), template)
                    self.assertNotIn("{{", prompt)

    def test_missing_value_raises(self):
        with self.assertRaises(ValueError):
            gp.fill_template("Hello {{name}}", {})

    def test_lists_become_bullets(self):
        self.assertEqual(gp.fill_template("{{items}}", {"items": ["a", "b"]}), "  - a\n  - b")

    def test_service_override(self):
        prompt = gp.build_prompt(gp.load_business("cafe"), "service_page", service="Desserts")
        self.assertIn("Service to write about: Desserts", prompt)

    def test_default_service_is_first_in_list(self):
        prompt = gp.build_prompt(gp.load_business("salon"), "service_page")
        self.assertIn("Service to write about: Haircut and styling", prompt)


if __name__ == "__main__":
    unittest.main()
