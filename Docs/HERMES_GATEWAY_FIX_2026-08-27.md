# Hermes TUI "gateway exited" — Diagnosis & Fix (2026-08-27)

**Symptom:** TUI footer showed `gateway exited` after sending any message; worked all morning in JetBrains Rider. Banner: `Melusina v0.20.6 (2026.8.27)` · `longcat 2.0:free` · `22.9k/131.1k 17%` · `voice off` · cwd `C:\EnvironmentPortfolio`.

**Status on inspection:** Daemon gateway was healthy — `C:\Users\froma\AppData\Local\hermes\gateway_state.json:1` `pid 35088 gateway_state:running exit_reason:null` (started `2026-08-27T19:08:52 --replace`, `discord:connected as zunda#6844`). `C:\Users\froma\AppData\Local\hermes\logs\gateway.log:350` showed `Gateway running with 1 platform(s)` with clean `kanban dispatcher: embedded`. No daemon crash.

**What was crashing:** The *TUI child* `tui_gateway\entry.py:487` (`python -m tui_gateway.entry`), not the daemon. Each TUI session spawns this child to bridge `sys.stdin`/`sys.stdout` JSON to the daemon.

**Evidence:**

- `C:\Users\froma\AppData\Local\hermes\logs\tui_gateway_crash.log:1` — repeated every 1–7 min all day:
  ```
  OSError: [Errno 22] Invalid argument
    File "C:\Users\froma\AppData\Local\hermes\hermes-agent\tui_gateway\entry.py", line 487, in main
      raw = sys.stdin.readline()
  exitCode=1 → [lifecycle] scheduling gateway reconnect in 1000ms
  ```
  alternating with `exitCode=3221225786 (0xC000013A STATUS_CONTROL_C_EXIT)` + `graceful-exit received signal=SIGHUP killing gateway` when the TUI closed.

- `C:\Users\froma\AppData\Local\hermes\hermes-agent\tui_gateway\entry.py:486-508` prior code:
  ```python
  while True:
      raw = sys.stdin.readline()  # unhandled
      if not raw:
          if not handle_spurious_eof(...): break
  ```
  No `try: except OSError` around `readline()`. On Windows, a detached console / SIGHUP / Rider-→-Windows-Terminal switch invalidates the stdin handle → `EINVAL` propagates as unhandled traceback, parent logs `transport exit code=1`, TUI shows `gateway exited` until the 1 s respawn.

- `C:\Users\froma\AppData\Local\hermes\hermes-agent\tui_gateway\_stdin_recovery.py:99-101` note: spurious-EOF recovery is POSIX-only (`fcntl`); on Windows it short-circuits to `return False` (genuine EOF) and never sees `EINVAL` — so the crash path was uncovered.

- `C:\Users\froma\AppData\Local\hermes\logs\agent.log:22` confirmed messages *did* reach the daemon: `20260827_151655_bf7888` `msg='HERMES IS BROKEN HELP'` completed `API call #1 8.4s`, `msg='gateway exited, longcat 2.0:free, 23.3k/131.1k 18%'` completed `API call #2 50.6s cache 99%` via `meituan/longcat-2.0:free` — the badge was stale, not a failed send.

- `C:\Users\froma\AppData\Local\hermes\logs\gateway-stdio.log:18` secondary factor: free-tier `meituan/longcat-2.0:free` intermittently timed out `TimeoutError 90s x3 = 277s no response from https://inference-api.nousresearch.com/v1` (seen `13:49:36`, `13:51:08`, `13:52:44`), making a gateway stall look like a death. `C:\Users\froma\AppData\Local\hermes\config.yaml:2` pins `model.default: meituan/longcat-2.0:free` — retained per owner preference (no model change in this fix).

**Why Rider worked:** Rider's embedded PTY keeps `sys.stdin` as a valid console handle. Outside Rider (Windows Terminal / detached `hermes` launch) the handle is a shared pipe that can be invalidated on `O_NONBLOCK` flips or console detach — exactly the `EINVAL` case.

**Fix applied (keeps longcat):**

- `C:\Users\froma\AppData\Local\hermes\hermes-agent\tui_gateway\entry.py:486-502` — wrap `readline()`:
  ```python
  try:
      raw = sys.stdin.readline()
  except (OSError, ValueError) as e:
      err_no = getattr(e, "errno", None)
      _log_exit(f"stdin readline {type(e).__name__}: {e} (errno={err_no})")
      break  # clean EOF — parent respawns in 1s without crash traceback
  ```
  Verified: `python -m py_compile entry.py` OK.

- `C:\Users\froma\AppData\Local\hermes\hermes-agent\tui_gateway\slash_worker.py:154-159` — same guard for the slash-command worker (`_sw_log` path), `py_compile` OK.

> **Caveat:** `hermes-agent\` is managed by `hermes update` — this patch will be overwritten on next Hermes release. Upstream fix is to merge the same `except OSError` into `tui_gateway/entry.py` (and `slash_worker.py`) so `EINVAL` is treated as clean EOF rather than unhandled crash.

**Verification:**

- `py_compile` passed for both files.
- Daemon still `running` (`gateway_state.json:1` `pid 35088`); `tasklist` shows `35088` + `mcp-helper` `8940`/`33924` + `tui_gateway` child `36696`.
- Next TUI session's `tui_gateway_crash.log` should show `gateway exit · reason=stdin readline OSError: ... (errno=22)` instead of `=== unhandled exception ===` + traceback, and the footer should recover within 1 s without stuck `gateway exited`.

**Optional (not applied, owner keeps longcat free):** To hide free-tier stalls while keeping longcat primary, uncomment `fallback_model` in `config.yaml:120` (e.g. `provider: nous` `model: deepseek/deepseek-v3.2` or an `openrouter` model). No change made per `2026-08-27` preference.

**Reproduce:** `hermes` in Windows Terminal → send any message → observe `tui_gateway_crash.log` before/after patch. Compare Rider vs Windows Terminal `stdin_is_tty` + `handle` validity.

*Fixed 2026-08-27 during owner nap; longcat retained.*
