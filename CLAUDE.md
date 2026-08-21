When working on coding with me, follow this workflow.

## 1. Discuss First

- Always start by discussing a change with me. Don't write code or edit the PR doc until I give explicit approval of the plan we discussed.
- When I want to build a new feature, immediately confirm with me that we should create a new PR doc + PR for it, based on the template at `docs/pr-docs/template.md`.

## 2. Plan in a PR Doc

- Once I approve the plan, update the relevant PR planning doc in `docs/pr-docs` to capture the scope. Base new docs on `docs/pr-docs/template.md`.
- Order the checklist from least consequential/complex first to most consequential/complex last.
- Include focused manual smoke tests in the PR doc.
- If a PR doc starts covering distinct scopes, ask before splitting it.

## 3. Branch When Ready

- Create a branch from current `main`, carry the approved changes into it, push to origin, and open a filled-in PR.
- Branch naming convention: `<type>/<pithy-theme-with-dashes>`.
- Use the PR Doc Open skill when opening the PR.
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
- Check CI when decision-relevant and wait for it before reporting a PR ready.

## 9. This Repository

- This is a plain static HTML/CSS site (no framework, no build step), published through `.github/workflows/publish.yaml`.
- Verify changes by opening the relevant `.html` file(s) directly in a browser.
- The nav is generated from `templates/nav.html` via `scripts/sync-nav.py` — edit the template, not individual pages' nav blocks.
- Enable `.githooks/pre-commit` once per clone (`git config core.hooksPath .githooks`) to keep the nav and resume download count synced automatically.
- Treat publishing to `main`/GitHub Pages as a production deployment requiring named confirmation.
