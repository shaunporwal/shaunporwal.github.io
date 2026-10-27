# PYTHON is `python3` by default. Set it to `uv run --no-project python` to run the
# generators and tests with uv.
PYTHON ?= python3

# One target per generator, so `make -k sync` (the pre-commit hook) still runs
# the rest when one fails. sync-dcurves overwrites a placeholder that
# sync-resume writes, so it depends on it.
SYNC_TARGETS := sync-resume sync-record sync-dcurves sync-theme sync-icon sync-nav sync-footer sync-seo sync-social sync-home \
	sync-blog-index sync-sitemap sync-crawler-files sync-agent-files sync-llms-full sync-feed sync-manifest sync-script-index

.PHONY: dev lint test sync $(SYNC_TARGETS) resume-text pdf

dev:
	./scripts/dev.sh

lint:
	ruff check .
	$(PYTHON) -m unittest discover -s tests -p "test_code_shape.py"

test: lint
	$(PYTHON) -m unittest discover -s tests -p "test_*.py"
	bash tests/test_update_dcurves_downloads.sh

sync: $(SYNC_TARGETS)

sync-resume:
	$(PYTHON) scripts/gen_resume.py

sync-record:
	$(PYTHON) scripts/gen_record.py

sync-dcurves: sync-resume
	./scripts/update-dcurves-downloads.sh

sync-theme:
	$(PYTHON) scripts/gen_theme.py

sync-icon:
	$(PYTHON) scripts/gen_icon.py

sync-nav:
	$(PYTHON) scripts/sync_nav.py

sync-footer:
	$(PYTHON) scripts/sync_footer.py

sync-seo:
	$(PYTHON) scripts/sync_seo.py

sync-social:
	$(PYTHON) scripts/sync_social.py

sync-home:
	$(PYTHON) scripts/sync_home.py

sync-blog-index:
	$(PYTHON) scripts/gen_blog_index.py

sync-sitemap:
	$(PYTHON) scripts/gen_sitemap.py

sync-crawler-files:
	$(PYTHON) scripts/gen_crawler_files.py

sync-agent-files:
	$(PYTHON) scripts/gen_agent_files.py

sync-llms-full:
	$(PYTHON) scripts/gen_llms_full.py

sync-feed:
	$(PYTHON) scripts/gen_feed.py

sync-manifest:
	$(PYTHON) scripts/gen_manifest.py

sync-script-index:
	$(PYTHON) scripts/gen_script_index.py

resume-text:
	$(PYTHON) scripts/gen_resume.py --text

pdf:
	$(PYTHON) scripts/render_pdf.py
