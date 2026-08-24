# Melodia Elite Live-Ops Source-Control Pipeline

> Trunk-based development keeps `main` always shippable while release/hotfix branches provide the isolation live-ops teams need.

## 2. CI/CD Gate Pipeline

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `liveops-ci.yml` | push/PR to `main` when `liveops/`, validators, or site assets change | Validates banner math, economy JSON, feature flags, site facts |
| `lfs-guard.yml` | every PR | Ensures lockable binaries are tracked by LFS and, locally, locked |
| `security.yml` | push/PR | Dependency review + TruffleHog secret scan |
| `pages.yml` | push to `main` | Vite build, gacha validation, asset validation, deploy to GitHub Pages + optional Wix |
| `liveops-release.yml` | manual | Bumps `VERSION`, updates `CHANGELOG.md`, opens `release/vX.Y.Z` PR |
| `liveops-hotfix.yml` | manual | Creates `hotfix/vX.Y.Z` branch from an existing release tag |

## 3. Gacha / Economy Validation

```powershell
python tools/validate_gacha.py --strict
python tools/validate_feature_flags.py
```

`validate_gacha.py` enforces:
- Banner IDs are UPPER_SNAKE_CASE.
- Pool rates sum to exactly `1.0`.
- `0 < soft_pity < hard_pity`.
- `guarantee_rarity` exists in pools.
- Featured items are present in a pool.
- Currency IDs are declared in `economy.json`.
- Overlapping banner schedules for the same currency are warned.

## 4. LFS & Binary Asset Governance

All `.uasset`, `.umap`, `.blend`, `.fbx`, textures, audio, fonts, and compiled modules are marked `lockable` in `.gitattributes`.

Before editing a binary file:

```powershell
git lfs lock BS_GodFile/Content/Melodia/Levels/L_KaleidoNave.umap
# ... edit ...
git add <file>
git commit -m "feat(level): tune KaleidoNave spawn density"
git lfs unlock BS_GodFile/Content/Melodia/Levels/L_KaleidoNave.umap
```

Local pre-commit hooks will block a commit if you modified a lockable binary without holding the lock.

## 5. Feature Flags

Runtime feature flags live in `liveops/feature_flags.json` and are consumed by the UE5 `UMelodiaFeatureFlagSubsystem` (see `.agents/worker_m3/gacha_git_liveops_workflow.md`).

## 6. Installing Local Hooks

```powershell
git config core.hooksPath .githooks
# or, if you prefer the pre-commit framework:
pre-commit install
```

## 7. Releasing

```powershell
# Manual via GitHub Actions workflow dispatch
# Or locally:
python tools/bump_version.py patch --message "fix economy refund rounding"
git push origin main --follow-tags
```

## 8. Connecting to GitHub

This workspace was initialized as a Git repository. To push to GitHub:

1. Create a new repository (e.g. `fromage3900/Melodia` or `fromage3900/EnvironmentPortfolio`).
2. Add it as origin: `git remote set-url origin https://github.com/fromage3900/<repo>.git`
3. Push: `git push -u origin main`

Existing sub-repositories (`BS_GodFile` -> `MelodiaMelusinaV2`, `my-site-clean` -> `my-site`) remain independent and can be linked later via git submodules if desired.
