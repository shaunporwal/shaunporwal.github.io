import copy
import json
import pathlib
import unittest

import context  # noqa: F401
import lib_record
import lib_site
from lib_schema import SchemaError

SAMPLE_RECORD = context.SAMPLE_RECORD


class TestFormatPeriod(unittest.TestCase):
    def test_resume_range(self):
        self.assertEqual(lib_record.format_period("2020-01", "2021-03", "resume"), "Jan 2020 – Mar 2021")

    def test_record_range(self):
        self.assertEqual(lib_record.format_period("2020-01", "2021-03", "record"), "January 2020 to March 2021")

    def test_present(self):
        self.assertEqual(lib_record.format_period("2020-01", "present", "resume"), "Jan 2020 – Present")

    def test_single_month(self):
        self.assertEqual(lib_record.format_period("2017-08", "2017-08", "record"), "August 2017")


class TestResumeView(unittest.TestCase):
    def setUp(self):
        self.view = lib_record.resume_view(SAMPLE_RECORD, context.FAKE_SITE)

    def test_contact_keeps_only_flagged_items(self):
        self.assertEqual(self.view["contact"], ["City, ST", "test@example.com"])

    def test_name_comes_from_site_data(self):
        self.assertEqual(self.view["name"], "Test Person")

    def test_experience_keeps_only_flagged_entries(self):
        self.assertEqual([e["org"] for e in self.view["experience"]], ["Acme"])

    def test_experience_meta_uses_resume_dates(self):
        self.assertEqual(self.view["experience"][0]["meta"], "Jan 2020 – Present · City, ST")

    def test_bullets_follow_overrides_flags_and_group_summaries(self):
        self.assertEqual(
            self.view["experience"][0]["bullets"],
            ["Short **detail**", "Group summary", "Kept as is", "Resume only"],
        )

    def test_education_override_and_honors(self):
        self.assertEqual(
            self.view["education"],
            [
                {
                    "degree": "B.S., Widgetry",
                    "school": "Acme University",
                    "meta": "May 2019 · City, ST",
                    "sub": "Cum laude",
                }
            ],
        )

    def test_project_links_join_into_one_row(self):
        self.assertEqual(
            self.view["projects"],
            [{"title": "Widget", "links": "[widget.com](https://example.com)", "description": "A widget."}],
        )

    def test_skills_use_overrides_and_derive_languages(self):
        self.assertEqual(
            self.view["skills"],
            {
                "Programming": "Python, Go",
                "Languages": "English (native); Mandarin Chinese, Hindi (fluent); Japanese (conversational)",
            },
        )

    def test_view_does_not_change_the_record(self):
        record = copy.deepcopy(SAMPLE_RECORD)
        lib_record.resume_view(record, context.FAKE_SITE)
        self.assertEqual(record, SAMPLE_RECORD)


class TestContactValue(unittest.TestCase):
    def test_a_literal_value_is_kept(self):
        self.assertEqual(lib_record.contact_value({"label": "Location", "value": "Town"}, context.FAKE_SITE), "Town")

    def test_email_is_plain_text(self):
        item = {"label": "Email", "site": "email"}
        self.assertEqual(lib_record.contact_value(item, context.FAKE_SITE), "test@example.com")

    def test_a_url_becomes_a_link_without_scheme_or_www(self):
        site = {**context.FAKE_SITE, "base_url": "https://www.example.com"}
        item = {"label": "Website", "site": "base_url"}
        self.assertEqual(lib_record.contact_value(item, site), "[example.com](https://www.example.com)")


    def test_schema_allows_exactly_the_keys_that_have_a_format(self):
        schema = json.loads((context.REPO_ROOT / "data" / "experiences.schema.json").read_text())
        allowed = schema["$defs"]["contact"]["properties"]["site"]["enum"]
        self.assertEqual(sorted(allowed), sorted(lib_record.SITE_CONTACT_FORMATS))


class TestLoadRecord(unittest.TestCase):
    def write_repo(self, record: dict) -> pathlib.Path:
        root = context.temp_repo(self)
        context.write_record_fixture(root, record)
        return root

    def test_loads_a_valid_record(self):
        self.assertEqual(lib_record.load_record(self.write_repo(SAMPLE_RECORD)), SAMPLE_RECORD)

    def test_rejects_an_invalid_record(self):
        record = copy.deepcopy(SAMPLE_RECORD)
        record["experience"][0]["start"] = "Jan 2020"
        with self.assertRaises(SchemaError):
            lib_record.load_record(self.write_repo(record))

    def test_rejects_a_bullet_with_no_text(self):
        record = copy.deepcopy(SAMPLE_RECORD)
        record["experience"][0]["groups"][0]["bullets"].append({})
        with self.assertRaises(SchemaError):
            lib_record.load_record(self.write_repo(record))

    def test_rejects_a_flag_on_a_bullet_with_no_text(self):
        record = copy.deepcopy(SAMPLE_RECORD)
        record["experience"][0]["groups"][0]["bullets"].append({"resume": True})
        with self.assertRaises(SchemaError):
            lib_record.load_record(self.write_repo(record))

    def test_the_real_record_is_valid_and_builds_a_resume(self):
        record = lib_record.load_record(context.REPO_ROOT)
        self.assertTrue(lib_record.resume_view(record, lib_site.load_site(context.REPO_ROOT))["experience"])


if __name__ == "__main__":
    unittest.main()
