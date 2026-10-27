import datetime
import json
import unittest

import context
import lib_jsonld

SITE = context.FAKE_SITE
RECORD = context.SAMPLE_RECORD
POST = {"title": "Hello", "excerpt": "An intro.", "date": datetime.date(2025, 3, 5)}


class TestPerson(unittest.TestCase):
    def test_has_the_profile_links_the_job_title_and_the_image(self):
        node = lib_jsonld.person(SITE, RECORD)
        self.assertEqual(node["@id"], "https://example.com/#person")
        self.assertEqual(node["jobTitle"], "Test engineer")
        self.assertEqual(node["image"], "https://example.com/media/avatar.jpg")
        self.assertEqual(node["sameAs"], [SITE["github"], SITE["x"], SITE["linkedin"]])

    def test_works_for_the_current_employer_with_its_project_url(self):
        node = lib_jsonld.person(SITE, RECORD)
        self.assertEqual(node["worksFor"], {"@type": "Organization", "name": "Acme Company", "url": "https://acme.example/"})

    def test_works_for_has_no_url_when_no_project_has_that_name(self):
        record = {**RECORD, "experience": [{**RECORD["experience"][0], "org": "Other Co"}]}
        self.assertEqual(lib_jsonld.person(SITE, record)["worksFor"], {"@type": "Organization", "name": "Other Co"})

    def test_has_no_works_for_when_no_role_is_current(self):
        record = {**RECORD, "experience": [RECORD["experience"][1]]}
        self.assertNotIn("worksFor", lib_jsonld.person(SITE, record))

    def test_never_holds_the_email_address(self):
        text = json.dumps(lib_jsonld.home_graph(SITE, RECORD)) + json.dumps(lib_jsonld.profile_page(SITE, RECORD))
        self.assertNotIn("test@example.com", text)
        self.assertNotIn("mailto", text)


class TestPages(unittest.TestCase):
    def test_home_graph_links_the_website_to_the_person_by_id(self):
        graph = lib_jsonld.home_graph(SITE, RECORD)["@graph"]
        self.assertEqual([node["@type"] for node in graph], ["WebSite", "Person"])
        self.assertEqual(graph[0]["publisher"], {"@id": graph[1]["@id"]})

    def test_profile_page_holds_the_person(self):
        page = lib_jsonld.profile_page(SITE, RECORD)
        self.assertEqual(page["@type"], "ProfilePage")
        self.assertEqual(page["mainEntity"]["@type"], "Person")

    def test_blog_posting_has_the_date_when_the_post_has_one(self):
        data = lib_jsonld.blog_posting(SITE, POST, "https://example.com/posts/h/", "https://example.com/i.png")
        self.assertEqual(data["datePublished"], "2025-03-05")
        self.assertEqual(data["author"]["name"], "Test Person")

    def test_blog_posting_without_a_date_has_no_date_field(self):
        data = lib_jsonld.blog_posting(SITE, {**POST, "date": None}, "u", "i")
        self.assertNotIn("datePublished", data)

    def test_breadcrumbs_run_from_the_home_page_to_the_post(self):
        crumbs = lib_jsonld.breadcrumbs(SITE, POST, "https://example.com/posts/h/")["itemListElement"]
        self.assertEqual([c["position"] for c in crumbs], [1, 2])
        self.assertEqual(crumbs[1]["item"], "https://example.com/posts/h/")


class TestScriptTag(unittest.TestCase):
    def test_cannot_close_its_script_tag(self):
        tag = lib_jsonld.script_tag({"headline": "A </script> title"})
        self.assertEqual(tag.count("</script>"), 1)


if __name__ == "__main__":
    unittest.main()
