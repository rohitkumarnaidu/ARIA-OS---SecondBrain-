## Summary
<!-- One sentence describing the change -->

## Related Issue
Closes #issue-number

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Refactor (no functional change)
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Infrastructure/DevOps

## Workstream
- [ ] WS-1: Design System
- [ ] WS-2: Component Library
- [ ] WS-3: Data Layer
- [ ] WS-4: Pages & Features
- [ ] WS-5: AI UX & Agents
- [ ] WS-6: Infrastructure

## Screenshots
<!-- Before/after for UI changes -->

## Quality Checklist

### Functionality
- [ ] Code does what it's supposed to do
- [ ] Edge cases handled (empty data, errors, timeouts)
- [ ] Error handling complete (try/catch everywhere)
- [ ] Supabase queries filtered by user_id

### Performance
- [ ] No N+1 queries
- [ ] Pagination for list endpoints
- [ ] AI calls wrapped with timeouts

### Testing
- [ ] New tests added for the change
- [ ] All existing tests still pass (`make test`)
- [ ] E2E tests pass for affected flows

### Style
- [ ] No `any` in TypeScript
- [ ] Design tokens used (no hardcoded colors)
- [ ] Imports ordered per convention
- [ ] No inline Pydantic models (use database/schemas/)

### Documentation
- [ ] Docs updated (if needed)
- [ ] Prompt version bumped (if changed)
- [ ] CHANGELOG.md updated

## Pre-Merge Checklist
- [ ] CI passes (all 6 jobs)
- [ ] At least 1 approval
- [ ] No unresolved conversations
- [ ] `make pre-commit` passes
