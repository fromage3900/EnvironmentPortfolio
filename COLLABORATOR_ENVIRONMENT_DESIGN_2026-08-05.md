# Live Collaborator Environment Design — 2026-08-05

**Status:** Planning draft  
**Goal:** Make `fromage3900/environment-portfolio` safe and fast for multiple live collaborators without requiring a full 300 GB checkout.

---

## Current State Summary

- `BS_GodFile/.git` is present and healthy at repo root.
- Latest local commit: `ec20b015` on `main`.
- `origin/main` and local `main` have diverged; local status shows 5 modified files pending commit/push verification.
- Existing collaborator guidance exists in `BS_GodFile/COLLABORATOR_SETUP.md`, but it needs tiered onboarding, cleanup, split-site strategy, and deploy verification.

---

## Recommended Decisions

1. **Backup retention:** Keep `.git.backup.mirror` (bare safety mirror). Drop the three large working clones: `.clone_v2`, `.temp_work`, `.transform_temp`.
2. **Website split:** Extract `BS_GodFile/my-site-clean` into a separate repo rather than a submodule, to reduce merge surface and LFS bloat in the game repo.

---

## Proposed Collaborator Tiers

### Tier 1: Lightweight Collaborator
- **Roles:** Level design, material art, UI work, documentation
- **Clone:** partial clone without LFS blobs
- **Sparse checkout:** only needed folders
- **LFS pull:** targeted asset types only
- **Typical size:** 2–10 GB
- **Setup time:** 10–15 minutes

### Tier 2: Full Build Collaborator
- **Roles:** Build engineer, packaging, PIE testing
- **Clone:** full clone with LFS
- **Typical size:** ~300 GB
- **Setup time:** 1–2 hours

### Tier 3: Code/ Docs Reviewer
- **Roles:** Code review, planning, documentation review
- **Clone:** without LFS
- **Typical size:** ~50 MB
- **Setup time:** ~1 minute

---

## Immediate Action Plan

1. **Push recovered `main`** to `origin` after verifying the active git path/repo state.
2. **Clean up dead clones** to reclaim disk space.
3. **Split `my-site-clean`** into its own repo.
4. **Verify GitHub Pages** deploy path/config.
5. **Update `COLLABORATOR_SETUP.md`** with tiered onboarding instructions.
6. **Add collaborator git hooks/validation** for LFS and file-size checks.
7. **Recover orphaned Python scripts** where possible.
8. **Address remaining P0 blockers:** save round-trip PIE proof and packaged build launch test.

---

## Parallel Documentation Updates Needed

- Refresh `TODO.md` and project dashboards to reflect current git state, backup decision, and site-split decision.
- Update handoff docs to note the collaborator tier model and onboarding commands.
- Ensure roadmap/blockers docs mention the website repo split and Pages verification status.

---

## Open Items

- Confirm exact origin push path/state if push continues to fail after repo-path verification.
- Confirm whether any collaborators need submodule access before finalizing split strategy.

---

## Actual State on 2026-08-05

- Git state: healthy local repo on `main` with recent checkpoint/recovery commits.
- Push status: **blocked by network/connectivity to `github.com:443`** in the current environment.
- Next move: complete offline-safe work and retry push from a network-available environment.