# -*- coding: utf-8 -*-
# ============================
# Ouroboros — Local Windows Runtime launcher (entry point, executed from repository)
# ============================
# Thin orchestrator: secrets, bootstrap, main loop.
# Heavy logic lives in supervisor/ package.

import logging
import os, sys, json, time, uuid, pathlib, subprocess, datetime, threading, queue as _queue_mod
from typing import Any, Dict, List, Optional, Set, Tuple

log = logging.getLogger(__name__)

# ----------------------------
# 0) Install launcher deps
# ----------------------------
def install_launcher_deps() -> None:
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "-q", "openai>=1.0.0", "requests"],
        check=True,
    )

install_launcher_deps()

def ensure_claude_code_cli() -> bool:
    """Best-effort install of Claude Code CLI for Anthropic-powered code edits."""
    # For Windows, try to install via npm if available
    try:
        # Check if npm is available
        subprocess.run(["npm", "--version"], check=True, capture_output=True, errors="replace")
        # Try to install Claude Code CLI globally
        subprocess.run(["npm", "install", "-g", "@anthropic-ai/claude-code"], check=False, errors="replace")
        # Check if claude command is now available
        result = subprocess.run(["claude", "--version"], check=False, capture_output=True, text=True, errors="replace")
        return result.returncode == 0
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("[launcher] Claude Code CLI installation failed or npm not available. Code editing features may be limited.")
        return False

# ----------------------------
# 0.1) provide apply_patch shim
# ----------------------------
from ouroboros.apply_patch import install as install_apply_patch
from ouroboros.llm import DEFAULT_LIGHT_MODEL
install_apply_patch()


if __name__ == '__main__':

    # ----------------------------
    # 1) Secrets + runtime config (Local version - uses environment variables)
    # ----------------------------
    _LEGACY_CFG_WARNED: Set[str] = set()

    def get_secret(name: str, default: Optional[str] = None, required: bool = False) -> Optional[str]:
        v = os.environ.get(name, default)
        if required:
            assert v is not None and str(v).strip() != "", f"Missing required secret: {name}"
        return v

    def get_cfg(name: str, default: Optional[str] = None, allow_legacy_secret: bool = False) -> Optional[str]:
        v = os.environ.get(name)
        if v is not None and str(v).strip() != "":
            return v
        return default

    def _parse_int_cfg(raw: Optional[str], default: int, minimum: int = 0) -> int:
        try:
            val = int(str(raw))
        except Exception:
            val = default
        return max(minimum, val)

    OPENROUTER_API_KEY = get_secret("OPENROUTER_API_KEY", required=True)
    TELEGRAM_BOT_TOKEN = get_secret("TELEGRAM_BOT_TOKEN", required=True)
    TOTAL_BUDGET_DEFAULT = get_secret("TOTAL_BUDGET", required=True)
    GITHUB_TOKEN = get_secret("GITHUB_TOKEN", required=True)

    # Robust TOTAL_BUDGET parsing — handles spaces and other junk
    try:
        TOTAL_BUDGET = float("".join(c for c in str(TOTAL_BUDGET_DEFAULT) if c.isdigit() or c == "."))
    except Exception:
        TOTAL_BUDGET = 50.0

    # Optional secrets
    OPENAI_API_KEY = get_secret("OPENAI_API_KEY")
    ANTHROPIC_API_KEY = get_secret("ANTHROPIC_API_KEY")

    # Runtime config
    OUROBOROS_MODEL = get_cfg("OUROBOROS_MODEL", "anthropic/claude-sonnet-4.6")
    OUROBOROS_MODEL_CODE = get_cfg("OUROBOROS_MODEL_CODE", "anthropic/claude-sonnet-4.6")
    OUROBOROS_MODEL_LIGHT = get_cfg("OUROBOROS_MODEL_LIGHT", DEFAULT_LIGHT_MODEL)
    OUROBOROS_WEBSEARCH_MODEL = get_cfg("OUROBOROS_WEBSEARCH_MODEL", "gpt-5")
    OUROBOROS_MODEL_FALLBACK_LIST = get_cfg("OUROBOROS_MODEL_FALLBACK_LIST", "anthropic/claude-sonnet-4.6,google/gemini-3-pro-preview,openai/gpt-4.1")

    OUROBOROS_MAX_WORKERS = _parse_int_cfg(get_cfg("OUROBOROS_MAX_WORKERS"), 5, 1)
    OUROBOROS_MAX_ROUNDS = _parse_int_cfg(get_cfg("OUROBOROS_MAX_ROUNDS"), 200, 1)
    OUROBOROS_BG_BUDGET_PCT = _parse_int_cfg(get_cfg("OUROBOROS_BG_BUDGET_PCT"), 10, 0)

    # Infrastructure
    OUROBOROS_WORKER_START_METHOD = get_cfg("OUROBOROS_WORKER_START_METHOD", "spawn")  # Windows-safe default
    OUROBOROS_DIAG_HEARTBEAT_SEC = _parse_int_cfg(get_cfg("OUROBOROS_DIAG_HEARTBEAT_SEC"), 30, 1)
    OUROBOROS_DIAG_SLOW_CYCLE_SEC = _parse_int_cfg(get_cfg("OUROBOROS_DIAG_SLOW_CYCLE_SEC"), 20, 1)

    # Local paths (no Google Drive)
    REPO_DIR = pathlib.Path.cwd()
    DRIVE_ROOT = REPO_DIR / "data"  # Use local data directory instead of Google Drive
    LOGS_DIR = DRIVE_ROOT / "logs"
    SNAPSHOTS_DIR = DRIVE_ROOT / "snapshots"

    # Ensure directories exist
    DRIVE_ROOT.mkdir(exist_ok=True)
    LOGS_DIR.mkdir(exist_ok=True)
    SNAPSHOTS_DIR.mkdir(exist_ok=True)

    # ----------------------------
    # 2) Initialize supervisor modules
    # ----------------------------
    from supervisor.state import (
        init as state_init, load_state, save_state, append_jsonl,
        update_budget_from_usage, status_text, rotate_chat_log_if_needed,
        init_state,
    )
    state_init(DRIVE_ROOT, TOTAL_BUDGET)
    init_state()

    from supervisor.telegram import (
        init as telegram_init, TelegramClient, send_with_budget, log_chat,
    )
    TG = TelegramClient(str(TELEGRAM_BOT_TOKEN))
    telegram_init(
        drive_root=DRIVE_ROOT,
        total_budget_limit=TOTAL_BUDGET,
        budget_report_every=10,  # Default value
        tg_client=TG,
    )

    from supervisor.git_ops import (
        init as git_ops_init, ensure_repo_present, checkout_and_reset,
        sync_runtime_dependencies, import_test, safe_restart,
    )
    REMOTE_URL = f"https://{GITHUB_TOKEN}:x-oauth-basic@github.com/{os.environ.get('GITHUB_USER')}/{os.environ.get('GITHUB_REPO')}.git"
    BRANCH_DEV = os.environ.get("OUROBOROS_BOOT_BRANCH", "ouroboros")
    BRANCH_STABLE = f"{BRANCH_DEV}-stable"
    git_ops_init(
        repo_dir=REPO_DIR, drive_root=DRIVE_ROOT, remote_url=REMOTE_URL,
        branch_dev=BRANCH_DEV, branch_stable=BRANCH_STABLE,
    )

    from supervisor.queue import (
        init as queue_init, enqueue_task, enforce_task_timeouts, enqueue_evolution_task_if_needed,
        persist_queue_snapshot, restore_pending_from_snapshot,
        cancel_task_by_id, queue_review_task, sort_pending,
    )
    queue_init(
        drive_root=DRIVE_ROOT,
        soft_timeout=300,  # Default soft timeout
        hard_timeout=600,  # Default hard timeout
    )

    from supervisor.workers import (
        init as workers_init, get_event_q, WORKERS, PENDING, RUNNING,
        spawn_workers, kill_workers, assign_tasks, ensure_workers_healthy,
        handle_chat_direct, _get_chat_agent, auto_resume_after_restart,
    )
    workers_init(
        repo_dir=REPO_DIR, drive_root=DRIVE_ROOT, max_workers=OUROBOROS_MAX_WORKERS,
        soft_timeout=300, hard_timeout=600,  # Default timeouts
        total_budget_limit=TOTAL_BUDGET,
        branch_dev=BRANCH_DEV, branch_stable=BRANCH_STABLE,
    )

    from supervisor.events import dispatch_event

    # ----------------------------
    # 3) Initialize supervisor components
    # ----------------------------
    from supervisor.telegram import (
        init as telegram_init, TelegramClient, send_with_budget, log_chat,
    )
    TG = TelegramClient(str(TELEGRAM_BOT_TOKEN))
    telegram_init(
        drive_root=DRIVE_ROOT,
        total_budget_limit=TOTAL_BUDGET,
        budget_report_every=10,  # Default value
        tg_client=TG,
    )

    from supervisor.git_ops import (
        init as git_ops_init, ensure_repo_present, checkout_and_reset,
        sync_runtime_dependencies, import_test, safe_restart,
    )
    git_ops_init(
        repo_dir=REPO_DIR, drive_root=DRIVE_ROOT, remote_url=REMOTE_URL,
        branch_dev=BRANCH_DEV, branch_stable=BRANCH_STABLE,
    )

    from supervisor.queue import (
        enqueue_task, enforce_task_timeouts, enqueue_evolution_task_if_needed,
        persist_queue_snapshot, restore_pending_from_snapshot,
        cancel_task_by_id, queue_review_task, sort_pending,
    )

    from supervisor.workers import (
        init as workers_init, get_event_q, WORKERS, PENDING, RUNNING,
        spawn_workers, kill_workers, assign_tasks, ensure_workers_healthy,
        handle_chat_direct, _get_chat_agent, auto_resume_after_restart,
    )
    workers_init(
        repo_dir=REPO_DIR, drive_root=DRIVE_ROOT, max_workers=OUROBOROS_MAX_WORKERS,
        soft_timeout=300, hard_timeout=600,  # Default timeouts
        total_budget_limit=TOTAL_BUDGET,
        branch_dev=BRANCH_DEV, branch_stable=BRANCH_STABLE,
    )

    from supervisor.events import dispatch_event
    from supervisor.state import load_state, append_jsonl

    # ----------------------------
    # 4) Bootstrap repo
    # ----------------------------
    ensure_repo_present()
    ok, msg = safe_restart(reason="bootstrap", unsynced_policy="rescue_and_reset")
    assert ok, f"Bootstrap failed: {msg}"

    # ----------------------------
    # 5) Start workers
    # ----------------------------
    kill_workers()
    spawn_workers(OUROBOROS_MAX_WORKERS)
    restored_pending = restore_pending_from_snapshot()
    persist_queue_snapshot(reason="startup")
    if restored_pending > 0:
        st_boot = load_state()
        if st_boot.get("owner_chat_id"):
            send_with_budget(int(st_boot["owner_chat_id"]),
                             f"[RESTART] Restored pending queue from snapshot: {restored_pending} tasks.")

    append_jsonl(LOGS_DIR / "supervisor.jsonl", {
        "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "type": "launcher_start",
        "branch": load_state().get("current_branch"),
        "sha": load_state().get("current_sha"),
        "max_workers": OUROBOROS_MAX_WORKERS,
        "model_default": OUROBOROS_MODEL, "model_code": OUROBOROS_MODEL_CODE, "model_light": OUROBOROS_MODEL_LIGHT,
        "soft_timeout_sec": 300, "hard_timeout_sec": 600,
        "worker_start_method": OUROBOROS_WORKER_START_METHOD,
        "diag_heartbeat_sec": OUROBOROS_DIAG_HEARTBEAT_SEC,
        "diag_slow_cycle_sec": OUROBOROS_DIAG_SLOW_CYCLE_SEC,
    })

    # ----------------------------
    # 5.1) Auto-resume after restart
    # ----------------------------
    auto_resume_after_restart()

    # ----------------------------
    # 5.2) Background consciousness
    # ----------------------------
    from ouroboros.consciousness import BackgroundConsciousness

    def _get_owner_chat_id() -> Optional[int]:
        try:
            st = load_state()
            cid = st.get("owner_chat_id")
            return int(cid) if cid else None
        except Exception:
            return None

    _consciousness = BackgroundConsciousness(
        drive_root=DRIVE_ROOT,
        repo_dir=REPO_DIR,
        event_queue=get_event_q(),
        owner_chat_id_fn=_get_owner_chat_id,
    )

    # ----------------------------
    # 5.3) Direct-mode watchdog
    # ----------------------------
    def _chat_watchdog_loop():
        soft_warned = False
        while True:
            time.sleep(OUROBOROS_DIAG_HEARTBEAT_SEC)
            try:
                agent = _get_chat_agent()
                if not agent._busy:
                    soft_warned = False
                    continue
                now = time.time()
                idle_sec = now - agent._last_progress_ts
                total_sec = now - agent._task_started_ts
                if idle_sec >= 600:
                    st = load_state()
                    if st.get("owner_chat_id"):
                        send_with_budget(int(st["owner_chat_id"]),
                                         f"[ALERT] Chat agent hung (idle {idle_sec:.0f}s, total {total_sec:.0f}s). Killing...")
                    kill_workers()
                    break
                if idle_sec >= 300 and not soft_warned:
                    st = load_state()
                    if st.get("owner_chat_id"):
                        send_with_budget(int(st["owner_chat_id"]),
                                         f"[WARN] Chat agent slow (idle {idle_sec:.0f}s, total {total_sec:.0f}s). Still working...")
                    soft_warned = True
            except Exception:
                log.exception("Watchdog error")

    _chat_watchdog_thread = threading.Thread(target=_chat_watchdog_loop, daemon=True)
    _chat_watchdog_thread.start()

    # ----------------------------
    # 5.4) Supervisor command handler
    # ----------------------------
    def _handle_supervisor_command(text: str, chat_id: int, tg_offset: int = 0):
        lowered = text.strip().lower()
        if lowered.startswith("/panic"):
            send_with_budget(chat_id, "[PANIC] PANIC: stopping everything now.")
            kill_workers()
            st2 = load_state(); st2["tg_offset"] = tg_offset; save_state(st2)
            raise SystemExit("PANIC")
        if lowered.startswith("/restart"):
            st2 = load_state(); st2["session_id"] = uuid.uuid4().hex; st2["tg_offset"] = tg_offset; save_state(st2)
            send_with_budget(chat_id, "[RESTART] Restarting (soft).")
            ok2, msg2 = safe_restart(reason="owner_restart", unsynced_policy="rescue_and_reset")
            if not ok2:
                send_with_budget(chat_id, f"[WARN] Restart cancelled: {msg2}")
                return True
            kill_workers()
            import os as _os; _os.execv(sys.executable, [sys.executable] + sys.argv)
        if lowered.startswith("/status"):
            status = status_text(WORKERS, PENDING, RUNNING, 300, 600)
            send_with_budget(chat_id, status)
            return "[Supervisor handled /status]\n"
        if lowered.startswith("/review"):
            queue_review_task(reason="owner:/review", force=True)
            return "[Supervisor handled /review — review task queued]\n"
        if lowered.startswith("/evolve"):
            parts = lowered.split()
            action = parts[1] if len(parts) > 1 else "on"
            turn_on = action not in ("off", "stop", "0")
            st2 = load_state(); st2["evolution_mode_enabled"] = bool(turn_on); save_state(st2)
            if not turn_on:
                PENDING[:] = [t for t in PENDING if str(t.get("type")) != "evolution"]
                persist_queue_snapshot(reason="evolve_off")
            send_with_budget(chat_id, f"[EVOLVE] Evolution: {'ON' if turn_on else 'OFF'}")
            return f"[Supervisor handled /evolve — evolution toggled {'ON' if turn_on else 'OFF'}]\n"
        if lowered.startswith("/bg"):
            parts = lowered.split()
            action = parts[1] if len(parts) > 1 else "status"
            if action in ("start", "on", "1"):
                send_with_budget(chat_id, f"[BG] {_consciousness.start()}")
            elif action in ("stop", "off", "0"):
                send_with_budget(chat_id, f"[BG] {_consciousness.stop()}")
            else:
                send_with_budget(chat_id, f"[BG] Background consciousness: {'running' if _consciousness.is_running else 'stopped'}")
            return "[Supervisor handled /bg]\n"
        return ""

    # Auto-start background consciousness
    try:
        _consciousness.start()
        log.info("[BG] Background consciousness auto-started")
    except Exception as e:
        log.warning("consciousness auto-start failed: %s", e)

    # ----------------------------
    # 5.5) Event context
    # ----------------------------
    import types as _types
    _event_ctx = _types.SimpleNamespace(
        DRIVE_ROOT=DRIVE_ROOT, REPO_DIR=REPO_DIR,
        BRANCH_DEV=BRANCH_DEV, BRANCH_STABLE=BRANCH_STABLE,
        TG=TG, WORKERS=WORKERS, PENDING=PENDING, RUNNING=RUNNING,
        MAX_WORKERS=OUROBOROS_MAX_WORKERS,
        send_with_budget=send_with_budget, load_state=load_state,
        save_state=save_state, update_budget_from_usage=update_budget_from_usage,
        append_jsonl=append_jsonl, enqueue_task=enqueue_task,
        cancel_task_by_id=cancel_task_by_id, queue_review_task=queue_review_task,
        persist_queue_snapshot=persist_queue_snapshot, safe_restart=safe_restart,
        kill_workers=kill_workers, spawn_workers=spawn_workers,
        sort_pending=sort_pending, consciousness=_consciousness,
    )

    # ----------------------------
    # 5.6) Main loop with Telegram polling
    # ----------------------------
    offset = int(load_state().get("tg_offset") or 0)
    _last_message_ts: float = time.time()
    _ACTIVE_MODE_SEC: int = 300

    while True:
        loop_started_ts = time.time()
        rotate_chat_log_if_needed(DRIVE_ROOT)
        ensure_workers_healthy()

        # Drain worker events
        event_q = get_event_q()
        while True:
            try:
                evt = event_q.get_nowait()
                dispatch_event(evt, _event_ctx)
            except _queue_mod.Empty:
                break

        enforce_task_timeouts()
        enqueue_evolution_task_if_needed()
        assign_tasks()
        persist_queue_snapshot(reason="main_loop")

        # Poll Telegram
        _active = (time.time() - _last_message_ts) < _ACTIVE_MODE_SEC
        _poll_timeout = 0 if _active else 10
        try:
            updates = TG.get_updates(offset=offset, timeout=_poll_timeout)
        except Exception as e:
            append_jsonl(LOGS_DIR / "supervisor.jsonl", {
                "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "type": "telegram_poll_error", "offset": offset, "error": repr(e),
            })
            time.sleep(1.5)
            continue

        for upd in updates:
            offset = int(upd["update_id"]) + 1
            msg = upd.get("message") or upd.get("edited_message") or {}
            if not msg:
                continue
            chat_id = int(msg["chat"]["id"])
            from_user = msg.get("from") or {}
            user_id = int(from_user.get("id") or 0)
            text = str(msg.get("text") or "")
            now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

            st = load_state()
            if st.get("owner_id") is None:
                st["owner_id"] = user_id
                st["owner_chat_id"] = chat_id
                st["last_owner_message_at"] = now_iso
                save_state(st)
                log_chat("in", chat_id, user_id, text)
                send_with_budget(chat_id, "[OK] Owner registered. Ouroboros online.")
                continue

            if user_id != int(st.get("owner_id")):
                continue

            log_chat("in", chat_id, user_id, text)
            st["last_owner_message_at"] = now_iso
            _last_message_ts = time.time()
            save_state(st)

            if text.strip().lower().startswith("/"):
                try:
                    result = _handle_supervisor_command(text, chat_id, tg_offset=offset)
                    if result is True:
                        continue
                    elif result:
                        text = result + text
                except SystemExit:
                    raise
                except Exception:
                    log.warning("Supervisor command error", exc_info=True)

            if not text:
                continue

            _consciousness.inject_observation(f"Owner message: {text[:100]}")
            agent = _get_chat_agent()
            if agent._busy:
                agent.inject_message(text)
            else:
                _consciousness.pause()
                def _run_task_and_resume(cid, txt):
                    try:
                        handle_chat_direct(cid, txt, None)
                    finally:
                        _consciousness.resume()
                _t = threading.Thread(target=_run_task_and_resume, args=(chat_id, text), daemon=True)
                try:
                    _t.start()
                except Exception as _te:
                    log.error("Failed to start chat thread: %s", _te)
                    _consciousness.resume()

        st = load_state()
        st["tg_offset"] = offset
        save_state(st)

        loop_dur = time.time() - loop_started_ts
        if OUROBOROS_DIAG_SLOW_CYCLE_SEC > 0 and loop_dur >= float(OUROBOROS_DIAG_SLOW_CYCLE_SEC):
            append_jsonl(LOGS_DIR / "supervisor.jsonl", {
                "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "type": "main_loop_slow_cycle",
                "duration_sec": round(loop_dur, 3),
            })
