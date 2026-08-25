# Next PC Setup — Handoff

Written 2026-08-25. Everything below was verified against disk and remotes in
the session that produced it. Where something is unverified or blocked, it says so.

## 0. Read this first — two things are NOT backed up

1. **`G:\Zundamons-kItchen-V2` has ~5,633 uncommitted insertions.**
   113 files were staged but the commit FAILED with git object corruption:
   `error: invalid object 100644 e73bc4964e28e881fb94436efd3af37fab420b53 for '.vscode/extensions.json'`
   The work is still on the drive, staged, not committed, not pushed.
   Repair procedure is in section 6.

2. **`G:\MelodiaMelusina\MelusinaFinalRig` is 24 GB of .blend files with no git at all.**
   150 blend files, no version control, offline-only. This is the Melusina rig
   history. Decide a strategy before trusting it to one drive.

G: was unplugged mid-session, so neither item could be finished.

## 1. What IS safe on GitHub

| Repo | Remote | State |
|---|---|---|
| EnvironmentPortfolio | `fromage3900/EnvironmentPortfolio` | branch `feature/zenforest-musical-glam` @ `264940f`, clean |
| BS_GodFile | `fromage3900/MelodiaMelusinaV2` | `main` @ `88c6b11c` pushed; `feature/zenforest-glam-headless` @ `2bb016fb` pushed |

Verified by `git ls-remote` — local and remote hashes matched.

Also pushed this session: `feature/echo-topo-chapter2` (1 commit that was local-only).

`wix/` (nested in EnvironmentPortfolio) is committed locally at `7bfc50d` but has
**no remote** — 13 files incl. 5 .glb + 3 .fbx models. It is one drive failure from gone.

## 2. Toolchain on the old PC (match or beat these)

Verified by `--version` on 2026-08-25:

```
git      2.48.1.windows.1
git-lfs  3.6.1
node     v24.18.0
npm      11.16.0
python   3.11.15   <- `python` on PATH
python3  3.14.5    <- NOTE: `python3` and `python` are DIFFERENT versions here
uv       0.12.5
gh       2.94.0
Blender  4.2, 4.3, 4.5 installed (Melodia addons target 5.2 per project notes)
Unreal   5.8  (BS_GodFile.uproject EngineAssociation)
```

The `python` vs `python3` mismatch is a real trap — `pip` resolves to 3.11.
Pin the interpreter explicitly in scripts rather than relying on PATH order.

## 3. Clone order

BS_GodFile's `.git` is **25 GB** with **3,790 LFS-tracked files**. Budget the
disk and the time; do this one first and let it run.

```bash
# 1. install git-lfs BEFORE cloning, or pointers come down as text stubs
git lfs install

# 2. BS_GodFile — the big one
git clone https://github.com/fromage3900/MelodiaMelusinaV2.git BS_GodFile
cd BS_GodFile
git checkout main

# if LFS smudge fails with HTTP 404 on some objects, do NOT abandon the checkout:
git -c filter.lfs.smudge= -c filter.lfs.process= -c filter.lfs.required=false \
    reset --hard main

# 3. EnvironmentPortfolio
git clone https://github.com/fromage3900/EnvironmentPortfolio.git
cd EnvironmentPortfolio
git checkout feature/zenforest-musical-glam
```

BS_GodFile is expected to live at `<EnvironmentPortfolio>/BS_GodFile` — the parent
repo gitignores it as an independent repo, and `AGENTS.md` references `../PROJECT.md`.

## 4. Secrets you must recreate (never committed, by design)

`.gitignore` excludes these. Nothing will run correctly until they exist:

- `.env` and `.env.local` — copy `.env.local.example` as the shape
- `.mcp.json` (root) and `BS_GodFile/.mcp.json` — MCP server registrations
- `.opencode.json`, `.rider/mcp.json`

One secret was found and scrubbed this session: an OpenRouter key was hardcoded
as a fallback default in `scripts/daemon_content_gen.py:39`. GitHub push
protection caught it. It now reads env-only with an empty default. **Do not
reintroduce literal key defaults** — push protection will block the branch.

## 5. Verify the checkout actually works

```bash
cd EnvironmentPortfolio
npm install
npm run lint            # eslint
npm run verify:all      # lint:tokens + site facts + asset validation
npm run validate:liveops
pytest
```

Available npm scripts (from package.json): `dev`, `lint`, `lint:css`,
`lint:tokens`, `paths:wix`, `paths:github`, `verify:manifest`, `verify:all`,
`validate:liveops`, `validate:gacha`, `validate:flags`.

Note `postinstall` runs `wix sync-types`, which needs the Wix CLI.

Repo hooks are portable and already active via `core.hooksPath = .githooks`.
The pre-commit hook runs an **LFS lock guard** that will reject a commit touching
a lockable binary (`.png`, `.wav`, `.fbx`, `.uasset`, and friends per
`.gitattributes`) unless you hold the LFS lock. That is not a bug — either
`git lfs lock <path>` or keep the binary out of the commit.

## 6. When G: comes back — repair Zundamon V2

The drive holds 113 staged files that never committed. Do this before anything else.

```bash
cd G:/Zundamons-kItchen-V2

# 1. see how bad the object DB is
git fsck --no-dangling

# 2. the known-bad object is .vscode/extensions.json's blob.
#    That file is editor config, not game code — dropping it from the index
#    is safe and unblocks the commit.
git rm --cached .vscode/extensions.json

# 3. its hooks path is broken too: "cannot spawn .githooks/pre-commit".
#    Commit with hooks disabled rather than "fixing" it blind.
git -c core.hooksPath= commit -m "feat(companion+quest+vn): Zundamon VO, companion system, quest config, VN dialogue"

# 4. verify, then push
git log --stat -1
git push origin main
```

If `git fsck` reports more than that one object, stop and reassess — do not
force a commit over a broken pack. The content is worth more than the history.

What is in that pending work (from `git diff --cached --stat`):

- `CompanionConfig.lua` +450, `CompanionVisualConfig.lua` +193
- `QuestConfig.lua` +1036
- `VNDialogueData.lua` +813, `VNPortraitConfig.lua` +72
- `CookingController.lua` +1348, `CookingResultCard.client.lua` +623
- `ZundaSoundController.lua` (new), `CookingService.lua` +249,
  `ZundaroomsService.lua` +260
- `Rhythm` folder wired into `default.project.json`
- voicevox worker + manifest (generated `.wav`/`.mp3` correctly gitignored)

Reminder from prior sessions: **`G:\Zundamons-kItchen-V2` is authoritative**
(GitHub `fromage3900/Zundamons-Kitchen-V2`). `C:\Users\froma\Zundamons-kItchen`
is old V1 — never serve from it.

`C:\Users\froma\Desktop` is also a git repo pointed at the V1 remote and has
diverged (non-fast-forward, 36 dirty files that are just loose Desktop PNGs).
Left untouched deliberately. Consider `git init`-ing your Desktop out of that repo.

## 7. Network gotcha — github.com partial IP block on this connection

This bit two pushes in this session and cost real time. Symptom: `google.com`
returns 200 while `github.com` times out after ~21s, and LFS uploads die
mid-transfer. It is **not** a GitHub outage and not a git bug.

Cause: DNS round-robin hands out several A records for github.com, and only some
are firewalled on this connection. Probe result on 2026-08-25:

```
140.82.114.4   -> 200   OK
140.82.114.3   -> 000   BLOCKED
140.82.113.4   -> 000   BLOCKED
140.82.112.3   -> 200   OK
20.205.243.166 -> 200   OK
20.27.177.113  -> 200   OK
```

Re-probe on the new PC rather than trusting those IPs — the blocked set varies
by ISP and over time:

```bash
for ip in 140.82.114.4 140.82.114.3 140.82.113.4 140.82.112.3; do
  code=$(curl -sS -m 8 --resolve github.com:443:$ip -o /dev/null -w "%{http_code}" https://github.com 2>/dev/null)
  echo "$ip -> ${code:-000}"
done
```

Real fix is to point the adapter at a public resolver (needs an **admin** shell —
the agent cannot do this):

```
netsh interface ip show dns name="Wi-Fi"                      # capture current first
netsh interface ip set dns name="Wi-Fi" static 1.1.1.1        # apply
netsh interface ip set dns name="Wi-Fi" dhcp                  # revert if needed
```

Do NOT try `git -c http.curloptResolve=...` on this box — Git for Windows is
built against schannel and rejects it: `Unsupported SSL backend 'openssl'`.
Retrying the plain push until round-robin lands on a good IP does work, but it
is a coin flip, not a fix.

## 8. A concurrent lane is writing to BS_GodFile — do not force-push it

This changed the plan mid-session and is the reason BS_GodFile's history was
**not** split into isolated commits.

Evidence:

- I committed `37e8b197` (melodia_studio GN instruments + Gaea) at 16:39:36.
- `2bb016fb` (`feat(worldgen): add native Gaea Unreal export prep`, 244 lines in
  `Tools/WorldGen/prepare_gaea_unreal_export_native.ps1`) landed on the SAME
  branch at 16:42:40 — three minutes later, not by me.
- A fresh uncommitted edit to
  `Content/MelodiaIntegration/Narrative/MelodiaQuillHarmonyAwakening.qsc`
  appeared without me touching it.

Currently dirty in BS_GodFile (peer lane work — **leave it alone**):

```
 M Content/MelodiaIntegration/Narrative/MelodiaQuillHarmonyAwakening.qsc
 M Tools/generate_and_inject_content.py
 M Tools/test_melodia_first_dream_route_contract.py
?? post-checkout  post-commit  post-merge  pre-push
```

Rules that follow from this:

- **Never `git add -A` in BS_GodFile.** Stage explicit paths only, or you will
  swallow another lane's changeset into your commit.
- **Never force-push a shared BS_GodFile branch.** Rewriting `main` or
  `feature/zenforest-glam-headless` destroys the peer's commits.
- `file exists` is not `change exists`. Re-verify your own edits semantically
  before assuming they survived.
- Before declaring work uncommitted, check `git log --oneline -- <path>` — a peer
  using a broad add may already have committed it for you.

The four loose `post-checkout` / `post-commit` / `post-merge` / `pre-push` files
at the BS_GodFile root are stray copies of the `.githooks/` scripts. Harmless,
but they are untracked litter — likely a hook-install script that wrote to the
wrong directory. Worth deleting once you confirm `.githooks/` has the real ones.

## 9. What the commit split actually did

EnvironmentPortfolio's single 240-file `chore(sync)` commit was replaced with
five reviewable commits on `feature/zenforest-musical-glam`:

```
d678330  chore(repo): tooling config, hooks, and ignore rules          (14 files)
ca55f74  docs: project documentation, handoffs, and contributor guides (49)
bf5865b  feat(tooling): portfolio automation, validation, asset pipeline (71)
93b0f20  feat(site): portfolio front-end — pages, components, embeds     (80)
264940f  test(infra): pytest suites, eval reports, TouchDesigner        (38)
```

Safety net: **`backup/pre-split-20260825`** (`c8cbdc2`) is the pre-rewrite commit,
kept as a local branch. Delete it only once you're satisfied.

Verified no content was lost:

```bash
git diff --diff-filter=D --name-only backup/pre-split-20260825 HEAD   # -> 0 files
```

The split also *added* 12 files the original commit had dropped (5 escher `.png`,
7 chrono_synth `.wav`) — they are now proper LFS pointers instead of being
silently unstaged by the lock guard.

BS_GodFile branches holding unique work, for reference:

| Branch | Note |
|---|---|
| `main` | pushed, 10 commits rebased onto origin this session |
| `feature/zenforest-glam-headless` | pushed; peer lane also commits here |
| `feature/echo-topo-chapter2` | pushed this session (was local-only) |
| `recovery/melodia-main-sync-20260811` | **push FAILED** — see below |
| `cursor/model-lanes-agents-slim-f425` | behind 14, stale |

`recovery/melodia-main-sync-20260811` (2 commits) could not be pushed. It failed
after ~25 min on **missing LFS objects** — the local LFS store lacks blobs the
commits reference:

```
(missing) Content/Melodia/_PROJECT/04_Materials/Textures/sbs_-_seamless_space_backgrounds_.../Purple_Nebula_6_-_1024x1024.uasset
(missing) ... Blue_Nebula_8_-_1024x1024.uasset
(missing) ... Purple_Nebula_7_-_1024x1024.uasset
hint: Your push was rejected due to missing or corrupt local objects.
```

That branch is a 2026-08-11 snapshot. Do **not** set `lfs.allowincompletepush true`
to force it — that uploads a branch whose assets can never be restored. Either
recover those three `.uasset` files from the old machine or accept the branch as
local-only history and let it die with the drive.

## 10. Suggested first moves on the new PC

1. `git lfs install`, then clone BS_GodFile (long) and EnvironmentPortfolio.
2. Recreate `.env`, `.env.local`, `.mcp.json` from your password manager.
3. Run the section 5 verification block; fix anything red before starting work.
4. Probe the github.com IPs (section 7) and set DNS if you see the block.
5. Plug in G:, repair Zundamon V2 (section 6), push it.
6. Decide what to do about the 24 GB unversioned `MelusinaFinalRig` blend history.
7. Give `wix/` a remote, or fold it into the parent repo, so it stops being
   single-copy.

