# Contributing to Tagore

Thank you for your interest in contributing to Novel Generation Pipeline! Contributions are welcome, whether you're fixing a bug, improving an agent, refining prompts, improving documentation, or adding a new feature.

Please read this guide before opening a Pull Request.

## Development Workflow

This project uses two protected branches:

- **`main`** — stable/release branch.
- **`dev`** — active development branch and the default target for contributions.

> **Do not open Pull Requests directly against `main`.**

All contributions should be made through a Pull Request targeting `dev`.

The general workflow is:

```
main
  │
  └── dev
       │
       ├── feature/your-feature
       ├── fix/your-fix
       ├── docs/your-change
       └── refactor/your-change
```

After review and approval, your Pull Request will be merged into `dev`.

## Getting Started

### 1. Fork the repository

Create your own fork of the repository on GitHub.

### 2. Clone your fork

```bash
git clone https://github.com/<your-username>/<repository-name>.git
cd <repository-name>
```

### 3. Add the upstream repository

```bash
git remote add upstream https://github.com/<owner>/<repository-name>.git
```

You can verify your remotes with:

```bash
git remote -v
```

### 4. Create your branch from `dev`

Make sure your local `dev` branch is up to date before starting work:

```bash
git fetch upstream
git checkout dev
git pull upstream dev
```

Create a new branch from `dev`:

```bash
git checkout -b feature/your-feature-name
```

For example:

```bash
git checkout -b feature/improve-canon-guard
```

## Branch Naming

Please use descriptive branch names.

Recommended prefixes:

| Prefix       | Use for                                     |
|--------------|----------------------------------------------|
| `feature/`   | New functionality                             |
| `fix/`       | Bug fixes                                     |
| `refactor/`  | Code restructuring without changing behavior  |
| `docs/`      | Documentation changes                         |
| `test/`      | Tests or testing improvements                 |
| `prompt/`    | Prompt-related changes                        |
| `chore/`     | Maintenance or tooling changes                |

Examples:

```
feature/add-scene-summary
fix/checkpoint-resume
refactor/state-management
docs/improve-installation-guide
test/add-canon-guard-tests
prompt/improve-writer-prompt
chore/update-dependencies
```

Keep branch names short, descriptive, and lowercase.

## Before Making Changes

Make sure your environment is set up correctly.

Create and activate a virtual environment:

```bash
python -m venv venv
```

On Linux/macOS:

```bash
source venv/bin/activate
```

On Windows:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create your `.env` file from `_env` and configure your required API keys.

> **Never commit API keys, secrets, `.env` files, databases, or other sensitive information.**

## Making Changes

Before implementing a change, please consider:

- Does this change fit the project's goal?
- Is the change necessary, or can the existing behavior be improved instead?
- Does the README need to be updated?
- Does the change require tests or additional validation?

## Code Guidelines

Keep changes focused and easy to review.

### General

- Follow existing project structure and conventions.
- Prefer clear, readable Python over clever implementations.
- Keep functions and modules focused on one responsibility.
- Avoid unnecessary dependencies.
- Add comments when the reasoning behind code is not obvious.
- Do not introduce unrelated changes in the same Pull Request.

### Configuration

- Do not hard-code API keys or credentials.
- Avoid committing local configuration files containing secrets.

## Testing Your Changes

Before opening a Pull Request, run the project locally:

```bash
python main.py
```

Verify that the affected functionality works as expected, and pay particular attention to any area your change touches directly.

If you add tests, make sure they pass before submitting the Pull Request.

## Keep Your Branch Updated

If `dev` has changed while you are working, update your branch before opening or updating your Pull Request.

For example:

```bash
git fetch upstream
git checkout dev
git pull upstream dev
git checkout feature/your-feature-name
git merge dev
```

Resolve any conflicts locally and verify that your changes still work.

## Commit Messages

Write clear commit messages that explain what changed.

**Good examples:**

```
Add continuity validation for scene transitions
Fix checkpoint resume after human rejection
Improve writer prompt for character consistency
Update installation documentation
```

**Avoid vague messages such as:**

```
fix
changes
update stuff
```

Keep commits reasonably focused. Small, logical commits are easier to review.

## Pull Requests

When your work is ready:

### 1. Push your branch

```bash
git push origin feature/your-feature-name
```

### 2. Open a Pull Request

On GitHub, open a Pull Request with:

- **base:** `dev`
- **compare:** `feature/your-feature-name`

Make sure the base branch is `dev`, not `main`.

### 3. Describe your changes

A good Pull Request should explain:

- What did you change?
- Why was the change needed?
- How did you test it?
- Are there any limitations or known issues?

For example:

```markdown
## Summary

Fixes an issue where X did not behave as expected under Y condition.

## Changes

- Updated the relevant module/function.
- Added a regression test covering the fix.

## Testing

- Ran `python main.py`
- Verified the specific scenario is now handled correctly.

## Notes

No changes to the public API.
```

### Pull Request Checklist

Before submitting your PR, make sure:

- [ ] My branch was created from `dev`.
- [ ] My Pull Request targets `dev`, not `main`.
- [ ] I have tested my changes locally.
- [ ] I have not committed API keys or secrets.
- [ ] I have not committed `.env` or other sensitive configuration.
- [ ] I have not included unrelated changes.
- [ ] Existing functionality still works.
- [ ] I updated documentation where necessary.
- [ ] I added or updated tests where appropriate.
- [ ] My commit messages are clear.
- [ ] I have described the changes and testing in the Pull Request.

## Pull Request Review

All contributions are reviewed before being merged.

Maintainers may request:

- Code changes
- Additional tests
- Documentation updates
- Changes to the implementation approach
- Clarification about behavior or design decisions

Please respond to review comments and update your branch as needed.

You do not need to open a new Pull Request for every requested change. Push additional commits to the same branch and the existing Pull Request will update automatically.

## Important: `main` and `dev`

Both `main` and `dev` are protected branches.

### `dev`

`dev` is the integration branch for ongoing development.

Contributors should follow:

```
your branch → Pull Request → dev
```

### `main`

`main` represents the stable branch.

Contributors should **not** submit normal feature or bug-fix Pull Requests directly to `main`. The maintainers will handle promotion of reviewed changes from `dev` to `main`.

```
feature/fix branch
       │
       ▼
      dev
       │
       ▼
     main
```

## Generated Files and Local Data

The project may generate local files such as:

```
generated_novel.md
state_checkpoint.db
```

These are runtime artifacts and generally should not be included in Pull Requests unless a specific contribution requires them.

**Do not commit:**

- `.env`
- `*.db`
- API keys
- Credentials
- Private story data
- Personal generated output

Check your changes before pushing:

```bash
git status
git diff
```

## Reporting Bugs

When reporting a bug, please include enough information to reproduce it.

Useful information includes:

- What you expected to happen
- What actually happened
- Steps to reproduce the issue
- Python version
- Relevant error messages
- Which node or component appears to be affected
- Whether the issue occurs consistently

For LLM-related issues, include the relevant input/output or a minimal reproducible example when possible, while removing any API keys or private information.

## Suggesting Features

Feature suggestions are welcome.

A useful feature request should explain:

- The problem you are trying to solve.
- The proposed behavior.
- Why the feature would be useful.
- Any alternative approaches you considered.

For larger changes, please discuss the idea with the maintainers before spending significant time implementing it.

## Security

Do not report security vulnerabilities through a public Pull Request or public issue.

If you discover a security issue involving credentials, API keys, data exposure, or another security-sensitive problem, contact the project maintainer privately using the security contact provided by the repository.

**Never include secrets in issues, Pull Requests, logs, screenshots, or code.**

## Questions

If you are unsure about something, feel free to open a discussion or issue before making a large change.

When in doubt:

```
Create branch from dev
        ↓
Make focused changes
        ↓
Test locally
        ↓
Push branch
        ↓
Open PR → dev
        ↓
Address review
        ↓
Maintainer merges
```

---

Thank you for contributing to Tagore, the Novel Generation Pipeline! ❤️