# PR Checklist

## Scope

- [ ] The PR has one clear purpose.
- [ ] Follow-up work is captured in `docs/pr-docs`.
- [ ] The PR description and PR doc are synchronized.
- [ ] Related issues are linked or explicitly marked as follow-up.

## Code Quality

- [ ] Changed behavior has focused tests.
- [ ] Shared styles/content are reused rather than duplicated.
- [ ] No dead code, debug output, stale copies, or credentials are committed.

## Required Checks

- [ ] `quarto render`
- [ ] GitHub CI is green.

## Conditional Checks

- [ ] If navigation changed: every navbar link resolves in the rendered site.
- [ ] If Stripe embeds changed: Test Mode checkout opens the intended product and no secret key is present client-side.
- [ ] If external accounts or credentials changed: the exact action received named confirmation.

## Site Smoke Tests

- [ ] Existing Home, About, Stuff, Blog, and Docs navigation still works.
- [ ] Changed pages render at desktop and mobile widths.
- [ ] External links and hosted checkout redirects open the intended destinations.

## Merge Readiness

- [ ] The branch is sufficiently current for a clean merge.
- [ ] Rollback is documented for external-service or publishing changes.
- [ ] Shaun will perform the merge to `main`.
