---
name: Pull Request
about: Propose changes to the HNIR-CCP project
title: "[TYPE]: Short description"
labels: ''
assignees: ''
---

## Description

Please provide a clear and concise description of the changes in this pull request.

## Related Issues

Link any related issues using keywords like `Closes #`, `Fixes #`, `Resolves #`.

## Type of Change

Please mark the relevant options with an `x`:

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Refactor
- [ ] Other (please describe)

## Checklist for Reviewer

Please ensure the following items are addressed before merging:

### Code Review Checklist

- [ ] Code is well-commented and easy to understand.
- [ ] Code follows existing coding standards and style guides.
- [ ] Unit tests cover new functionality or bug fixes.
- [ ] All tests pass.
- [ ] Changes do not introduce new warnings or errors.

### Security and Safety Checklist

- [ ] **Ethical Review:** Have the ethical implications of this change been considered? (Refer to `ETHICS.md`)
    - Does this change have any potential for misuse?
    - Could this change introduce or exacerbate bias?
    - Is this change aligned with our project's ethical principles?
- [ ] **Policy Review:** Does this change align with the defined policies in `DATA_POLICY.md` and `GOVERNANCE.md`?
- [ ] **Safety Invariants:** Does this change uphold the [Safety Invariants Enforced by CCP](#safety-invariants-enforced-by-ccp)?
    - [ ] Destructive or irreversible actions require explicit user confirmation.
    - [ ] Policy-bound operations must pass all authorization and workflow validation steps.
    - [ ] Conversational state transitions must be deterministic and auditable.
    - [ ] LLM reasoning cannot bypass deterministic policy or control decisions.
    - [ ] Ambiguous control commands must trigger structured clarification rather than execution.
- [ ] **Destructive Actions:** If this PR involves destructive actions, is explicit human confirmation required?
- [ ] **Conflict Detection:** If new rules are added, have potential conflicts been considered and documented?

## Screenshots (if applicable)

If your changes involve UI updates or new features, please provide screenshots.
