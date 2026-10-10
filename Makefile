# One target per generator, so `make -k sync` (the pre-commit hook) still runs
# the rest when one fails. sync-dcurves overwrites a placeholder that
# sync-resume writes, so it depends on it.
SYNC_TARGETS := sync-resume sync-record sync-dcurves sync-nav sync-seo sync-social sync-blog-index sync-sitemap sync-crawler-files

.PHONY: dev lint test sync $(SYNC_TARGETS) resume-text

dev:
	./scripts/dev.sh

lint:
	ruff check .
	python3 -m unittest discover -s tests -p "test_code_shape.py"

test: lint
	python3 -m unittest discover -s tests -p "test_*.py"
	bash tests/test_update_dcurves_downloads.sh

sync: $(SYNC_TARGETS)

sync-resume:
	python3 scripts/gen_resume.py

sync-record:
	python3 scripts/gen_record.py

sync-dcurves: sync-resume
	./scripts/update-dcurves-downloads.sh

sync-nav:
	python3 scripts/sync_nav.py

sync-seo:
	python3 scripts/sync_seo.py

sync-social:
	python3 scripts/sync_social.py

sync-blog-index:
	python3 scripts/gen_blog_index.py

sync-sitemap:
	python3 scripts/gen_sitemap.py

sync-crawler-files:
	python3 scripts/gen_crawler_files.py

resume-text:
	python3 scripts/gen_resume.py --text
