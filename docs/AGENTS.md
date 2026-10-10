# docs/

This directory holds prose for people and agents.

## Files

- `development.md`: the full developer guide. It explains the data files, the generators, lint, and how to add a post or a page.
- `all-experiences.md`: the full experience record. `scripts/gen_record.py` writes the block between the `RECORD` markers from `data/experiences.json`. Edit the JSON file, never this block. You can edit the introduction above the block by hand.
- `pr-docs/`: one planning doc for each PR. `pr-docs/README.md` is the index. `pr-docs/archive/` holds the docs of merged PRs.

## Rules

- Write every doc in ASD-STE100 Simplified Technical English. Use short sentences, active voice, and one word for one meaning.
- Start a new PR doc from `pr-docs/template.md`. Name it `<PR number>-<slug>.md` after the PR opens.
- Order a PR doc checklist from the least to the most consequential change. Check off a task only after its tests pass.
- Keep the GitHub PR description in sync with the PR doc.
- After a PR merges, archive its doc with the PR Doc Archive skill.
- Do not restate a fact from `data/` by hand in a doc. Point to the source, or generate the text.
