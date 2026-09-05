from html.parser import HTMLParser
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]


class LandingParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
        self.text = []
        self.meta = {}

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        self.tags.append((tag, attributes))
        if tag == "meta":
            key = attributes.get("name") or attributes.get("property")
            if key:
                self.meta[key] = attributes.get("content", "")

    def handle_data(self, data):
        value = " ".join(data.split())
        if value:
            self.text.append(value)


class LandingPageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (ROOT / "index.html").read_text(encoding="utf-8")
        cls.css = (ROOT / "assets" / "styles.css").read_text(encoding="utf-8")
        cls.javascript = (ROOT / "assets" / "main.js").read_text(encoding="utf-8")
        cls.parser = LandingParser()
        cls.parser.feed(cls.html)
        cls.page_text = " ".join(cls.parser.text)

    def test_positioning_is_ai_work_transformation_not_code_refactoring(self):
        description = cls_description = self.parser.meta.get("description", "")
        self.assertIn("AI", description)
        self.assertTrue(
            any(term in description for term in ("工作流", "工作方式", "组织")),
            cls_description,
        )
        self.assertNotIn("AI 编程时代", self.html)
        self.assertNotIn("烂代码", self.page_text)

    def test_signature_visual_explains_a_three_stage_workflow_refactor(self):
        figures = [
            attrs
            for tag, attrs in self.parser.tags
            if tag == "figure" and "workflow-panel" in attrs.get("class", "").split()
        ]
        self.assertEqual(len(figures), 1)
        self.assertEqual(figures[0].get("id"), "workflow")
        self.assertEqual(figures[0].get("aria-labelledby"), "workflow-title")

        stages = {
            stage
            for tag, attrs in self.parser.tags
            if tag == "article"
            and "workflow-stage" in attrs.get("class", "").split()
            and (stage := attrs.get("data-stage"))
        }
        self.assertEqual(stages, {"before", "refactor", "after"})

        workflow_steps = [
            attrs
            for tag, attrs in self.parser.tags
            if tag == "li" and "workflow-step" in attrs.get("class", "").split()
        ]
        workflow_arrows = [
            attrs
            for tag, attrs in self.parser.tags
            if tag == "div" and "workflow-arrow" in attrs.get("class", "").split()
        ]
        replay_buttons = [
            attrs
            for tag, attrs in self.parser.tags
            if tag == "button"
            and "workflow-replay" in attrs.get("class", "").split()
        ]
        self.assertEqual(len(workflow_steps), 12)
        self.assertEqual(len(workflow_arrows), 2)
        self.assertEqual(len(replay_buttons), 1)
        self.assertEqual(
            replay_buttons[0].get("aria-label"),
            "重播工作流重构动画",
        )

    def test_offer_flow_remains_available(self):
        forms = [
            attrs
            for tag, attrs in self.parser.tags
            if tag == "form" and attrs.get("id") == "offer-form"
        ]
        self.assertEqual(len(forms), 1)
        self.assertIn("mailto:vague0307@gmail.com", self.html)

        field_names = {
            attrs.get("name")
            for tag, attrs in self.parser.tags
            if tag in {"input", "textarea"} and attrs.get("name")
        }
        self.assertEqual(field_names, {"name", "offer", "message"})
        self.assertIn('document.getElementById("offer-form")', self.javascript)
        self.assertIn('form.addEventListener("submit"', self.javascript)
        self.assertIn('mailto:vague0307@gmail.com', self.javascript)

    def test_workflow_markup_styles_and_animation_share_the_same_contract(self):
        self.assertIn('document.getElementById("workflow")', self.javascript)
        self.assertIn('panel.querySelector(".workflow-replay")', self.javascript)
        self.assertIn(
            'panel.querySelectorAll(".workflow-step, .workflow-arrow")',
            self.javascript,
        )

        for selector in (
            ".workflow-panel",
            ".workflow-stage",
            ".workflow-step",
            ".workflow-replay",
        ):
            self.assertIn(selector, self.css)

        reduced_motion = re.search(
            r"@media\s*\(prefers-reduced-motion:\s*reduce\)\s*\{(?P<body>.*?)\n\}",
            self.css,
            re.DOTALL,
        )
        self.assertIsNotNone(reduced_motion)
        self.assertIn(
            ".workflow-panel.play .workflow-step",
            reduced_motion.group("body"),
        )
        self.assertIn(
            ".workflow-panel.play .workflow-arrow",
            reduced_motion.group("body"),
        )


if __name__ == "__main__":
    unittest.main()
