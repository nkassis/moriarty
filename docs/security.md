# Repository security

What keeps secrets and junk off `main`, and what to do when a check fires.

## Rules

- `main` is protected: changes arrive by pull request; direct push and force-push are off; the `ci-ok` check must pass; the branch must be up to date with `main` before merge.
- No credentials in the tree. `infra/.env` is ignored; `infra/.env.example` is committed with placeholder values only. Provider keys live in the gateway's environment, never in a crew.
- No franchise names, ship names, registry numbers, insignia or stardates. Reviewers check this by hand; there is no linter for it.
- Docs changes carry the same bar as code: the writing standard in `docs/architecture.md` § Developer documentation.

## Secret scanning

Two layers, both TruffleHog with `--results=verified`, so a report means a credential that authenticated against its provider, not a regex match.

| Layer | When | Scope |
| --- | --- | --- |
| pre-commit hook | `git commit`, `git push` | staged diff / pushed range |
| GitHub Actions: `secret-scan` job in `ci.yml` | every PR and push to `main` | commits added by the PR or push |
| GitHub Actions: `secret-scan-push` in `secret-scan.yml` | push to any other branch | commits added by the push |

GitHub's own push protection is free only for public repositories (user-level protection) or with a paid GitHub Secret Protection licence on Team/Enterprise organizations. This repo is private under a personal account, so the pre-commit hook and the Actions are the two layers. When the repo goes public, user-level push protection applies automatically.

### Local setup

```sh
uv tool install pre-commit                    # or: pipx install pre-commit
uv run pre-commit install --hook-type pre-commit --hook-type pre-push
```

TruffleHog binary (the hook uses `language: system`):

```sh
# Linux / WSL
curl -sSfL https://raw.githubusercontent.com/trufflesecurity/trufflehog/main/scripts/install.sh | sh -s -- -b ~/.local/bin
trufflehog --version
```

### Full-history scan

Run once before the first push and after any history rewrite:

```sh
trufflehog git file://. --results=verified --fail
# or without installing:
docker run --rm -v "$PWD:/repo" trufflesecurity/trufflehog:latest git file:///repo --results=verified --fail
```

Exit code 0 means nothing verified. Exit 183 means a verified secret was found; the output names the commit and file.

### If a check fires

1. Rotate the credential first. Removing it from git does not un-leak it.
2. Remove it from the tree and commit.
3. If it is already on GitHub, rewrite history (`git filter-repo`) and force-push the branch; `main` has force-push off, so ask a repo admin or merge the rewrite through a PR after discussing. A leaked secret in `main` history is a rotate-and-move-on situation, not a reason to rewrite `main`.
4. Re-run the full-history scan.

False positives are rare with `--results=verified`. If one happens, exclude the path in a `.trufflehogignore` (regex per line) rather than turning the check off.

## Branch protection (settings, not code)

Settings → Branches → Add rule for `main`:

- Require a pull request before merging; 0 required approvals while it is one person, 1 when a second contributor joins.
- Require status checks to pass: `ci-ok` only. Require branches to be up to date.
- Require conversation resolution.
- Block force pushes. Do not allow deletions.
- Do not allow bypassing the above settings (includes admins).

The same via `gh`:

```sh
gh api -X PUT repos/nkassis/moriarty/branches/main/protection \
  --input - <<'JSON'
{
  "required_status_checks": {"strict": true, "contexts": ["ci-ok"]},
  "enforce_admins": true,
  "required_pull_request_reviews": {"required_approving_review_count": 0},
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "required_conversation_resolution": true
}
JSON
```

Required checks are an allowlist of job names, so each new job used to need a settings change; the aggregate keeps the list to one name. `ci-ok` in `ci.yml` needs every other job there and fails if any of them failed, was cancelled or was skipped:

| Job | Runs |
| --- | --- |
| `python-check` | ruff, black --check, pytest, contract schema drift, licences |
| `bridge-check` | tsc, ESLint, Stylelint, Prettier, Vitest, token drift |
| `bridge-e2e` | Playwright screenshots of `/kit` in the Playwright container |
| `secret-scan` | TruffleHog, `--results=verified` |

A new CI job goes into `ci-ok`'s `needs:` in the same PR; the branch rule does not change.
