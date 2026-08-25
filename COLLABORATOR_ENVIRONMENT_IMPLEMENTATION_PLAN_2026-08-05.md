# Collaborator Environment Implementation Plan — 2026-08-05

## Completed
- Created `COLLABORATOR_ENVIRONMENT_DESIGN_2026-08-05.md`
- Updated `TODO.md` with live-collaborator tasks
- Added `BS_GodFile/deploy/collaborator_onboarding.sh`
- Added `BS_GodFile/deploy/validate_collaborator_setup.sh`
- Updated `BS_GodFile/COLLABORATOR_SETUP.md` with script references

## Next actions
1. Retry `git push origin main` from a network-available environment
2. Clean up `.clone_v2`, `.temp_work`, `.transform_temp`
3. Confirm backup retention: keep `.git.backup.mirror`
4. Split `BS_GodFile/my-site-clean` into a separate repo
5. Verify GitHub Pages deploy path/URL
6. Update `COLLABORATOR_SETUP.md` with tier details from the design doc
7. Add git hooks for LFS/size validation
8. Recover orphaned Python scripts where possible
9. Address save round-trip PIE proof and packaged build launch test

## Decisions needed
- `my-site-clean`: separate repo or submodule?
- GitHub Pages: this repo vs separate `my-site` repo?