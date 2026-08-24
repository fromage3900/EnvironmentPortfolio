## Summary
<!-- One-line description of the change -->

## Change Type
- [ ] Feature
- [ ] Bugfix
- [ ] Live-ops config (banner / economy / feature flag)
- [ ] Asset or shader
- [ ] CI/CD or tooling
- [ ] Documentation

## Pre-Flight Checklist
- [ ] I have acquired a `git lfs lock` for every binary file I edited (`.uasset`, `.umap`, `.blend`, `.fbx`, textures, audio, fonts).
- [ ] `python tools/validate_gacha.py` passes (if `liveops/` changed).
- [ ] `python tools/validate_feature_flags.py` passes (if `liveops/feature_flags.json` changed).
- [ ] `python tools/validate_assets.py` passes (if `generated/` assets changed).
- [ ] `python tools/_verify_site_facts.py` passes (if `wix/` or `content/` changed).
- [ ] `CHANGELOG.md` is updated for player-facing or pipeline-affecting changes.

## Risk & Rollback
- **Risk level:** Low / Medium / High
- **Rollback plan:** <!-- e.g., revert commit, disable feature flag, rollback banner JSON -->

## Screenshots / Evidence
<!-- For visual or live-ops changes, attach proof -->
