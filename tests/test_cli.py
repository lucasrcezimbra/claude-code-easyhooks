import json
import subprocess

import pytest

from easyhooks import Events, _cli, hook


@pytest.fixture
def pre_tool_use_write_input():
    return {
        "session_id": "abc123",
        "transcript_path": "/Users/.../.claude/projects/.../00893aaf-19fa-41d2-8238-13269b9b3ca0.jsonl",
        "cwd": "/Users/...",
        "hook_event_name": "PreToolUse",
        "tool_name": "Write",
        "tool_input": {"file_path": "/path/to/file.txt", "content": "file content"},
    }


@pytest.fixture
def pre_tool_use_bash_input():
    return {
        "session_id": "abc123",
        "transcript_path": "/Users/.../.claude/projects/.../00893aaf-19fa-41d2-8238-13269b9b3ca0.jsonl",
        "cwd": "/Users/...",
        "hook_event_name": "PreToolUse",
        "tool_name": "Bash",
        "tool_input": {
            "command": "ls",
            # TODO: confirm this input
        },
    }


def test_cli_installed():
    result = subprocess.run(
        ["cc-easyhooks"],
        input=json.dumps({}).encode(),
        capture_output=True,
    )

    assert result.returncode == 0


def test_cli_input(pre_tool_use_write_input):
    result = subprocess.run(
        ["cc-easyhooks"],
        input=json.dumps(pre_tool_use_write_input).encode(),
        capture_output=True,
    )

    assert result.returncode == 0


@pytest.mark.skip(
    reason="Failing because the bash_hook and the cli are running in different processes. TODO: define a way to test this."
)
def test_call_pre_tool_use_bash_hook(pre_tool_use_bash_input):
    test_list = []

    @hook([Events.PreToolUse.Bash])
    def bash_hook(input):
        test_list.append(input)

    result = subprocess.run(
        ["cc-easyhooks"],
        input=json.dumps(pre_tool_use_bash_input).encode(),
        capture_output=True,
    )

    assert result.returncode == 0
    print(result.stdout.decode())
    assert test_list == [pre_tool_use_bash_input]


def test_call_pre_tool_use_bash_hook_dont_call_other_hooks(pre_tool_use_bash_input):
    test_list = []

    @hook([Events.PreToolUse.Write])
    def write_hook(input):
        test_list.append(input)

    result = subprocess.run(
        ["cc-easyhooks"],
        input=json.dumps(pre_tool_use_bash_input).encode(),
        capture_output=True,
    )

    assert result.returncode == 0
    assert test_list == []


def test_cli_pre_tool_use_bash_hook(mocker, pre_tool_use_bash_input):
    test_list = []

    @hook([Events.PreToolUse.Bash])
    def bash_hook(input):
        test_list.append(("Bash", input))

    mocker.patch("sys.stdin.read", return_value=json.dumps(pre_tool_use_bash_input))

    _cli()

    assert test_list == [("Bash", pre_tool_use_bash_input)]


def test_cli_pre_tool_use_write_hook(mocker, pre_tool_use_write_input):
    test_list = []

    @hook([Events.PreToolUse.Write])
    def write_hook(input):
        test_list.append(input)

    mocker.patch("sys.stdin.read", return_value=json.dumps(pre_tool_use_write_input))

    _cli()

    assert test_list == [pre_tool_use_write_input]


def test_cli_pre_tool_use_bash_hook_dont_call_other_hooks(
    mocker, pre_tool_use_bash_input
):
    test_list = []

    @hook([Events.PreToolUse.Write])
    def write_hook(input):
        test_list.append(input)

    mocker.patch("sys.stdin.read", return_value=json.dumps(pre_tool_use_bash_input))

    _cli()

    assert test_list == []


def test_multiple_events(mocker, pre_tool_use_bash_input):
    test_list = []

    @hook([Events.PreToolUse.Bash])
    def bash_hook(input):
        test_list.append(("bash_hook", input))

    @hook([Events.PreToolUse.Write])
    def write_hook(input):
        test_list.append(("write_hook", input))

    mocker.patch("sys.stdin.read", return_value=json.dumps(pre_tool_use_bash_input))

    _cli()

    assert test_list == [("bash_hook", pre_tool_use_bash_input)]


def test_multiple_hooks_same_event(mocker, pre_tool_use_bash_input):
    test_list = []

    @hook([Events.PreToolUse.Bash])
    def bash_hook1(input):
        test_list.append(("bash_hook1", input))

    @hook([Events.PreToolUse.Bash])
    def bash_hook2(input):
        test_list.append(("bash_hook2", input))

    mocker.patch("sys.stdin.read", return_value=json.dumps(pre_tool_use_bash_input))

    _cli()

    assert test_list == [
        ("bash_hook1", pre_tool_use_bash_input),
        ("bash_hook2", pre_tool_use_bash_input),
    ]
