# Team GitHub Workflow

## Branching Strategy

- The `main` branch contains stable, production-ready code.
- Each new feature is developed in its own branch.
- Branch naming conventions:
  - feature/<description>
  - fix/<description>
  - docs/<description>
  - refactor/<description>
  - chore/<description>
- Branches are deleted after they are merged.

## Commit Message Convention

Format:

[type]: description

Types used:
- feat
- fix
- docs
- refactor
- chore

Example:

feat: add viewer engagement tracking

Why:
This keeps the Git history clean and easy to understand.

## Pull Request Process

- Every change is submitted through a Pull Request.
- PRs should reference related GitHub Issues.
- At least one review is recommended before merging.
- Code review focuses on:
  - Correctness
  - Readability
  - Data integrity
  - Testing

## GitHub Issue Tracking

- Every feature or bug starts with a GitHub Issue.
- Each issue includes:
  - Title
  - Description
  - Label
  - Assignee
- Issues are closed when the related PR is merged using:
  - Closes #issue_number