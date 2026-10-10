If you have no context about this repo, read section 9 ("This Repository") first.

When working on coding with me, follow this workflow.

## 1. Discuss First

- Always start by discussing a change with me. Don't write code or edit the PR doc until I give explicit approval of the plan we discussed.
- When I want to build a new feature, immediately confirm with me that we should create a new PR doc + PR for it, based on the template at `docs/pr-docs/template.md`.

## 2. Plan in a PR Doc

- Once I approve the plan, update the relevant PR planning doc in `docs/pr-docs` to capture the scope. Base new docs on `docs/pr-docs/template.md`.
- Order the checklist from least consequential/complex first to most consequential/complex last.
- Include focused manual smoke tests in the PR doc.
- If a PR doc starts covering distinct scopes, ask before splitting it.
- Keep follow-up work in the current PR unless Shaun asks for a new one.

## 3. Branch When Ready

- Create a branch from current `main`, carry the approved changes into it, push to origin, and open a filled-in PR.
- Branch naming convention: `<type>/<pithy-theme-with-dashes>`.
- Use the PR Doc Open skill when opening the PR. Do this as soon as I approve the plan and the PR doc is written. Do not ask first. Do not wait for a separate "ready".
- Never merge to `main`. Shaun is the only person allowed to merge PRs to `main`.

## 4. Build with TDD

- Build UI-first: static presentation, then external-service wiring, then any business logic.
- Write failing tests that describe the approved behavior before implementation.
- Keep code DRY and orthogonal, reuse existing abstractions, and individually test new modular abstractions.
- Reuse shared constants instead of introducing duplicate inline literals.
- Keep experimental features additive and rollback-safe.
- Ask before work that cannot remain orthogonal or whose intent is uncertain.

## 5. Track Progress & Follow-Ups

- Check off a PR-doc task only after its tests pass.
- Confirm before adding discovered follow-up scope.
- Keep the GitHub PR description synchronized with meaningful PR-doc changes, including smoke tests and known issues.
- After a PR merges, mark its doc done, archive it, and update the PR-doc index using the PR Doc Archive skill.

## 6. Production-Mutating Commands Need Named Confirmation

- Before every deploy or command that mutates production data or infrastructure, ask for confirmation naming the exact command and effect.
- General approval of a plan does not authorize an individual production mutation.

## 7. Credential and Security-Sensitive Actions Need Named Confirmation

- Before creating accounts, generating credentials, registering keys/tokens, or changing payment-provider access, ask for confirmation naming the exact action.
- Never commit Stripe secrets or other live credentials. Public Stripe Payment Link and Buy Button identifiers may be committed only when intentionally approved.

## 8. Verification and Diagnostics Stay With the Agent

- Run checks directly and report results; do not ask Shaun to generate diagnostic output.
- Install a local tool that a check needs, such as a test browser, without asking. Ask first only when the install changes the repository or needs administrator rights.
- Check CI when decision-relevant and wait for it before reporting a PR ready.

## 9. This Repository

Read this section first if you have no other context. Then read the `AGENTS.md` in the directory where you work.

### What This Repo Is

This repo is Shaun Porwal's personal website, `https://www.shaunporwal.com`. It is plain static HTML and CSS. It has no framework and no build step. GitHub Pages serves the `site/` directory. A push to `main` publishes it through `.github/workflows/publish.yaml`. Only Shaun merges to `main`.

### Map

| Directory | Contents | Instructions |
|---|---|---|
| `data/` | JSON sources of truth and their schemas | [data/AGENTS.md](data/AGENTS.md) |
| `docs/` | Development guide, PR docs, the generated experience record | [docs/AGENTS.md](docs/AGENTS.md) |
| `scripts/` | Python generators and shared libraries | [scripts/AGENTS.md](scripts/AGENTS.md) |
| `site/` | The published website | [site/AGENTS.md](site/AGENTS.md) |
| `templates/` | HTML fragments stamped into pages | [templates/AGENTS.md](templates/AGENTS.md) |
| `tests/` | Unit tests, lint checks, and the print layout check | [tests/AGENTS.md](tests/AGENTS.md) |

Two hidden directories also matter. `.githooks/pre-commit` runs lint and regenerates files before each commit. `.github/workflows/` holds CI (`test.yaml`) and publishing (`publish.yaml`).

### How Content Flows

- Each fact has one source: a JSON file in `data/`, a template in `templates/`, or a post's own HTML.
- Generators in `scripts/` copy facts into the files that show them. A generated part of a file sits between `<!-- NAME:START -->` and `<!-- NAME:END -->` markers. Some files are fully generated, such as `site/sitemap.xml`.
- Never edit a generated block or a generated file. Edit its source, then run `make sync`.
- To find the source of a generated block, search `scripts/` for its marker name.

### Commands

- `make dev`: serve `site/` at `http://localhost:8000` with live reload.
- `make sync`: run every generator. The `Makefile` is the only list of generators and their order.
- `make lint`: run ruff and the code-shape check.
- `make test`: run lint, then every test.
- `make resume-text`: print the resume as plain text.
- Enable the pre-commit hook once per clone: `git config core.hooksPath .githooks`. Install ruff once: `uv tool install ruff`.

### Rules

- Treat publishing to `main` or GitHub Pages as a production deployment. It needs named confirmation.
- Keep each fact in one source. When a fact must show in a second place, generate it.
- Write all documentation, including every `AGENTS.md`, in ASD-STE100 Simplified Technical English.
- Fix a lint failure by restructuring the code. Do not raise a limit in `ruff.toml`.
- `data/experiences.json` is the single source of truth for every experience fact. It generates the resume and `docs/all-experiences.md`. The `resume` key on an item puts it on the resume.
- The resume has no page limit. Its print layout must never split an entry across pages, leave a heading alone at the bottom of a page, or break in any other unattractive way.
- The pre-commit hook regenerates files under `site/`, including the dcurves download count. This is normal. Do not report it or ask about it.
- When you add a top-level directory, add an `AGENTS.md` to it and a row to the map above. `tests/test_agents_docs.py` fails until you do.

For full details, read `docs/development.md`.
