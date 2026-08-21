.PHONY: dev test sync

dev:
	./scripts/dev.sh

test:
	python3 -m unittest discover -s tests -p "test_*.py"
	bash tests/test_update_dcurves_downloads.sh

sync:
	python3 scripts/sync_nav.py
	python3 scripts/sync_seo.py
	python3 scripts/gen_blog_index.py
	python3 scripts/gen_sitemap.py
	./scripts/update-dcurves-downloads.sh
