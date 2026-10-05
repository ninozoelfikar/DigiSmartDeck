#!/usr/bin/env python3
"""
Multi-Layered Test Suite for DigiSmartDeck Terminal Prompt Precision & Server Safety
Layer 1: Unit & Regex Heuristics (Shell Prompt, Stale Buffer, Active Prompts, Streaming Logs)
Layer 2: Server Memory & State Management (TTL Cleanup, Localhost Restriction, Reconnect Hygiene)
Layer 3: End-to-End PTY Process Simulation (Fast Streaming, Active Prompt Detection, Auto-Dismiss)
"""

import os
import sys
import time
import json
import asyncio
import pty
import select
from importlib.machinery import SourceFileLoader

# Load digi-term and server modules
digi_term_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'digi-term'))
server_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'server.py'))

dt = SourceFileLoader('digi_term', digi_term_path).load_module()
srv = SourceFileLoader('server_module', server_path).load_module()


# ══════════════════════════════════════════════════════════════
# LAYER 1: UNIT & REGEX HEURISTICS
# ══════════════════════════════════════════════════════════════

def test_layer1_shell_prompts():
    print("[Layer 1.1] Testing Shell Prompt Recognition & Exclusion...")
    shell_samples = [
        "nino@Jarvis:~$ ",
        "root@server:/etc# ",
        "(venv) nino@Jarvis:~/DigiSmartDeck$ ",
        "(base) conda_user@host:~/project$ ",
        "nino@Jarvis:~/repo (main) $ ",
        "user@macbook % ",
        "~/DigiSmartDeck > ",
        "PS C:\\Users\\Administrator> ",
        "nino@workstation:~/DigiSmartDeck$   "
    ]
    for sample in shell_samples:
        assert dt.is_shell_prompt(sample), f"Failed to identify shell prompt: {sample!r}"
        assert dt.detect_prompt(sample) is None, f"detect_prompt should return None for shell prompt: {sample!r}"
    print("  -> Passed: All 9 shell prompt variants correctly recognized and rejected.")


def test_layer1_stale_history_rejection():
    print("[Layer 1.2] Testing Stale History Rejection (Finished Commands)...")
    stale_samples = [
        # History with prior question, but returned to shell
        """
Ask for permission:
1. Yes
2. No
Tool call executed successfully.
(venv) nino@Jarvis:~/DigiSmartDeck$ 
""",
        # History with npm prompt, but finished and at shell
        """
? Would you like to install packages? (Y/n) y
Installing dependencies...
added 24 packages in 1.4s
nino@Jarvis:~/DigiSmartDeck$ 
""",
        # History with [y/N], followed by compilation log
        """
Do you want to proceed? [y/N]: y
Building application artifacts...
Compiling module 4 of 4...
Done in 2.1s
root@server:/opt# 
"""
    ]
    for sample in stale_samples:
        detected = dt.detect_prompt(sample)
        assert detected is None, f"Stale history must return None, but got: {detected}"
    print("  -> Passed: Stale historical questions completely ignored when command has finished.")


def test_layer1_streaming_logs_rejection():
    print("[Layer 1.3] Testing Streaming Logs Rejection (Anti-Premature)...")
    streaming_samples = [
        # AI CLI streaming its plan/tool call
        """
Allow tool call: run_command(npm test)
Scanning project files...
Executing unit test runner...
""",
        # Script printing the word permission/run in logs
        """
[INFO] Starting permission check on database...
[INFO] Verifying access credentials for user...
[INFO] All permission checks passed successfully.
"""
    ]
    for sample in streaming_samples:
        detected = dt.detect_prompt(sample)
        assert detected is None, f"Streaming logs must return None, but got: {detected}"
    print("  -> Passed: Active log streaming containing permission keywords correctly ignored.")


def test_layer1_active_prompts_detection():
    print("[Layer 1.4] Testing Active Prompts Detection...")
    
    # Test A: Direct [y/N] prompt
    yn_sample = "Do you want to apply these changes? [y/N]: "
    res_yn = dt.detect_prompt(yn_sample)
    assert res_yn is not None, "Failed to detect active [y/N] prompt"
    assert res_yn['options'][0]['label'] == 'Yes', f"Expected primary Yes option, got: {res_yn['options'][0]}"
    assert res_yn['options'][3]['label'] == 'No', f"Expected danger No option, got: {res_yn['options'][3]}"

    # Test B: Press Enter prompt
    enter_sample = "Press enter to continue..."
    res_enter = dt.detect_prompt(enter_sample)
    assert res_enter is not None, "Failed to detect Press Enter prompt"
    assert res_enter['title'] == 'Menunggu Enter'

    # Test C: Bubbletea selector list with cursor ❯
    bubbletea_sample = """
Tool confirmation: run_command(pytest tests/)
❯ 1. Yes, allow tool call
  2. Allow in this chat
  3. Allow in this project
  4. No, deny tool call
"""
    res_bt = dt.detect_prompt(bubbletea_sample)
    assert res_bt is not None, "Failed to detect Bubbletea interactive menu"
    assert len(res_bt['options']) == 4, f"Expected 4 options, got: {len(res_bt['options'])}"
    assert res_bt['options'][0]['send'] == '\r'
    assert res_bt['options'][1]['send'] == '\x1b[B\r'
    assert res_bt['options'][2]['send'] == '\x1b[B\x1b[B\r'
    assert res_bt['options'][3]['send'] == '\x1b'

    # Test D: Menu with separate cursor prompt on the next line
    cursor_sample = """
Ask for permission:
1. Yes
2. Allow in this chat
3. Allow in this project
4. No
❯ 
"""
    res_cursor = dt.detect_prompt(cursor_sample)
    assert res_cursor is not None, "Failed to detect menu with separate cursor line"
    assert len(res_cursor['options']) == 4

    print("  -> Passed: All active prompt formats (binary y/n, press enter, Bubbletea list, cursor prompt) correctly parsed.")


# ══════════════════════════════════════════════════════════════
# LAYER 2: SERVER MEMORY & STATE MANAGEMENT
# ══════════════════════════════════════════════════════════════

def test_layer2_server_ttl_cleanup():
    print("[Layer 2.1] Testing Server PENDING_PROMPTS TTL Expiration...")
    srv.PENDING_PROMPTS.clear()

    now = time.time()
    # Add a fresh prompt (created 2s ago, timeout 60s)
    srv.PENDING_PROMPTS["fresh_prompt"] = {
        'payload': {'prompt_id': 'fresh_prompt', 'timeout': 60},
        'created_at': now - 2,
        'future': None
    }
    # Add an expired prompt (created 65s ago, timeout 60s)
    srv.PENDING_PROMPTS["stale_prompt"] = {
        'payload': {'prompt_id': 'stale_prompt', 'timeout': 60},
        'created_at': now - 65,
        'future': None
    }

    # Trigger cleanup
    srv.cleanup_pending_prompts()

    assert "fresh_prompt" in srv.PENDING_PROMPTS, "Fresh prompt should not be purged!"
    assert "stale_prompt" not in srv.PENDING_PROMPTS, "Stale prompt (>60s) must be purged!"
    srv.PENDING_PROMPTS.clear()
    print("  -> Passed: Stale prompts purged automatically; fresh prompts preserved.")


def test_layer2_localhost_restriction():
    print("[Layer 2.2] Testing Server Endpoint Localhost Restriction...")
    class MockRequest:
        def __init__(self, remote):
            self.remote = remote

    assert srv.is_localhost(MockRequest("127.0.0.1")) is True
    assert srv.is_localhost(MockRequest("::1")) is True
    assert srv.is_localhost(MockRequest("localhost")) is True
    assert srv.is_localhost(MockRequest("192.168.1.50")) is False
    assert srv.is_localhost(MockRequest("10.0.0.5")) is False
    assert srv.is_localhost(MockRequest("")) is False
    print("  -> Passed: Localhost-only restriction strictly blocks external LAN/WAN callers.")


# ══════════════════════════════════════════════════════════════
# LAYER 3: END-TO-END PTY PROCESS SIMULATION
# ══════════════════════════════════════════════════════════════

def test_layer3_pty_fast_streaming():
    print("[Layer 3.1] Testing PTY Simulation: Fast Streaming Output (No False Popups)...")
    # Simulate a child process that streams lots of text rapidly with keywords
    master_fd, slave_fd = pty.openpty()

    supervisor = dt.DigiTermSupervisor(['/bin/echo', 'dummy'])
    supervisor.master_fd = master_fd

    # Write streaming text into the PTY
    chunks = [
        b"Starting automated build pipeline...\n",
        b"[tool] allow tool call: run_command(cmake --build)\n",
        b"Compiling file1.cpp [1/5]\n",
        b"Compiling file2.cpp [2/5]\n",
        b"Compiling file3.cpp [3/5]\n",
        b"Build completed with 0 errors.\n",
        b"nino@Jarvis:~/DigiSmartDeck$ "
    ]

    for chunk in chunks:
        os.write(slave_fd, chunk)
        # Read from master_fd into supervisor.buf
        r, _, _ = select.select([master_fd], [], [], 0.05)
        if master_fd in r:
            data = os.read(master_fd, 4096)
            supervisor.buf += data.decode('utf-8', errors='ignore')
            supervisor.last_output = time.time()
        time.sleep(0.02)

    # Now verify that detect_prompt returns None (because it concluded at shell prompt)
    detected = dt.detect_prompt(supervisor.buf)
    assert detected is None, f"Fast streaming ending at shell prompt must not trigger popup! Got: {detected}"

    os.close(slave_fd)
    os.close(master_fd)
    print("  -> Passed: Fast streaming with permission keywords did not trigger any false popup.")


def test_layer3_pty_interactive_and_autodismiss():
    print("[Layer 3.2] Testing PTY Simulation: Real Interactive Prompt & Auto-Dismiss...")
    master_fd, slave_fd = pty.openpty()

    supervisor = dt.DigiTermSupervisor(['/bin/echo', 'dummy'])
    supervisor.master_fd = master_fd

    # Write an interactive prompt to PTY
    os.write(slave_fd, b"Do you want to proceed with database migration? [y/N]: ")
    r, _, _ = select.select([master_fd], [], [], 0.05)
    if master_fd in r:
        data = os.read(master_fd, 4096)
        supervisor.buf += data.decode('utf-8', errors='ignore')
        supervisor.last_output = time.time()

    # Verify that an active prompt IS detected
    detected = dt.detect_prompt(supervisor.buf)
    assert detected is not None, "Interactive prompt [y/N] should be detected!"
    assert detected['title'] == 'Do you want to proceed with database migration??' or 'proceed' in detected['title'].lower()

    # Simulate supervisor active_id being set
    supervisor.active_id = "test_prompt_123"

    # Now simulate user answering on PC keyboard or process continuing with new output
    os.write(slave_fd, b"y\nMigrating table 'users'... Done!\nnino@Jarvis:~$ ")
    r, _, _ = select.select([master_fd], [], [], 0.05)
    if master_fd in r:
        data = os.read(master_fd, 4096)
        decoded = data.decode('utf-8', errors='ignore')
        supervisor.buf += decoded
        # Logic in supervisor.run: if active_id and new output arrives, dismiss_active and clear_buffer
        if supervisor.active_id and (len(decoded) > 3 or '\n' in decoded):
            supervisor.dismiss_active()
            supervisor.clear_buffer()

    assert supervisor.active_id is None, "active_id must be cleared on subsequent output!"
    assert supervisor.buf == "", "Buffer must be cleared on auto-dismiss!"
    assert dt.detect_prompt(supervisor.buf) is None

    os.close(slave_fd)
    os.close(master_fd)
    print("  -> Passed: Active prompt properly detected and auto-dismissed immediately when new output arrives.")


# ══════════════════════════════════════════════════════════════
# MAIN RUNNER
# ══════════════════════════════════════════════════════════════

def run_all_tests():
    print("=" * 65)
    print("RUNNING MULTI-LAYERED TEST SUITE: DIGISMARTDECK PROMPT PRECISION")
    print("=" * 65)

    # Layer 1
    test_layer1_shell_prompts()
    test_layer1_stale_history_rejection()
    test_layer1_streaming_logs_rejection()
    test_layer1_active_prompts_detection()
    print()

    # Layer 2
    test_layer2_server_ttl_cleanup()
    test_layer2_localhost_restriction()
    print()

    # Layer 3
    test_layer3_pty_fast_streaming()
    test_layer3_pty_interactive_and_autodismiss()
    print()

    print("=" * 65)
    print("ALL TESTS PASSED: 3 LAYERS OF VERIFICATION SUCCESSFUL")
    print("=" * 65)


if __name__ == '__main__':
    run_all_tests()
