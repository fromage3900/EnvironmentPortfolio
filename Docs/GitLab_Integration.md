# GitLab Integration

This document describes how the EnvironmentPortfolio monorepo is mirrored to GitLab and how the GitLab CI/CD pipeline is configured.

## 1. Why a GitLab mirror?

- **Redundant CI:** GitHub Actions and GitLab CI run the same validation jobs, so a failure on one platform is visible on both.
- **Built-in LFS and secret scanning:** GitLab has native LFS support and Secret Detection that complement our GitHub workflows.
- **Release MRs:** GitLab CI can prepare release branches and open merge requests automatically, mirroring the GitHub release workflow.

## 2. Repository setup

The local repository should have two remotes:

```bash
git remote -v
# origin    https://github.com/fromage3900/EnvironmentPortfolio.git (fetch)
# origin    https://github.com/fromage3900/EnvironmentPortfolio.git (push)
# gitlab    https://gitlab.com/<your-user-or-group>/EnvironmentPortfolio.git (fetch)
# gitlab    https://gitlab.com/<your-user-or-group>/EnvironmentPortfolio.git (push)
```

Add the GitLab remote manually (replace the URL with your actual project):

```bash
git remote add gitlab https://gitlab.com/<your-user-or-group>/EnvironmentPortfolio.git
```

## 3. Safe mirror helper

Use `tools/git_mirror.py` to push to both remotes safely. It checks for divergence and dirty state before pushing.

```bash
# Check remotes and divergence only
python tools/git_mirror.py --check

# Check and push to both origin and gitlab
python tools/git_mirror.py --all
```

The helper refuses to push if:

- either `origin` or `gitlab` remote is missing,
- the working tree is dirty,
- either remote is ahead of the local branch (requires a pull/merge first).

## 4. GitLab CI pipeline

The pipeline is defined in `.gitlab-ci.yml` and mirrors the four GitHub Actions workflows:

| Stage | Job | Equivalent GitHub workflow | Trigger |
|---|---|---|---|
| `validate` | `validate:gacha` | `liveops-ci.yml` | MR/push changes to `liveops/` or `tools/validate_gacha.py` |
| `validate` | `validate:feature-flags` | `liveops-ci.yml` | MR/push changes to `liveops/` or `tools/validate_feature_flags.py` |
| `validate` | `site:integrity` | `liveops-ci.yml` | MR/push changes to `generated/` or site validators |
| `audit` | `lfs:audit` | `lfs-guard.yml` | Every MR / manual |
| `security` | `security:secret-scan` | `security.yml` | Every MR / manual |
| `release` | `release:prepare` | `liveops-release.yml` | Manual pipeline with `BUMP` variable |

### Run a manual release

1. Go to **CI/CD > Pipelines** in GitLab.
2. Click **Run pipeline**.
3. Set variable `BUMP` to `patch`, `minor`, or `major`.
4. The pipeline creates a `release/vX.Y.Z` branch and opens an MR to `main`.

## 5. Merge request template

The default MR template is in `.gitlab/merge_request_templates/default.md`. It enforces:

- Conventional Commit type,
- impact tag for `liveops` changes,
- local LFS guard and live-ops validation checks,
- a reminder not to commit secrets.

## 6. Troubleshooting

### GitLab CI cannot find git-lfs

The `lfs:audit` job installs `git-lfs` with `apt-get`. If you are using a custom runner, ensure the image has `git-lfs` installed.

### Secret scan job fails on a false positive

The TruffleHog job only fails on **verified** secrets. If a false positive is reported, add it to the repository's allowlist or use GitLab's native Secret Detection allowlist.

### Release MR creation fails

The `release:prepare` job uses `CI_JOB_TOKEN` to create the MR. Ensure the project setting **CI/CD > Token Access** allows the job to access the API, or switch to a project access token stored in `GITLAB_TOKEN`.

## 7. Notes

- `.gitlab-ci.yml` uses the `python:3.11` Docker image for validation jobs.
- The GitLab mirror is **push-only**; the local repo is still the source of truth.
- Do not force-push to `gitlab` unless you have also coordinated the same history rewrite on `origin`.
