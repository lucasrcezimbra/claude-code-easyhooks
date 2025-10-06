import json
import subprocess
from pathlib import Path

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


def call_cli(input):
    return subprocess.run(
        ["cc-easyhooks", (Path(__file__).resolve().parent / "easyhooks")],
        input=json.dumps(input).encode(),
        capture_output=True,
    )


def test_cli_input(pre_tool_use_write_input):
    result = call_cli(pre_tool_use_write_input)
    assert result.returncode == 0


def test_custom_easyhooks_path(pre_tool_use_bash_input):
    result = call_cli(pre_tool_use_bash_input)
    assert result.returncode == 0
    assert result.stdout.decode() == "Printing command: ls\n"


def test_cli_pre_tool_use_bash_hook(mocker, pre_tool_use_bash_input):
    test_list = []

    @hook(Events.PreToolUse.Bash)
    def bash_hook(input):
        test_list.append(("Bash", input))

    mocker.patch("sys.stdin.read", return_value=json.dumps(pre_tool_use_bash_input))

    _cli()

    assert test_list == [("Bash", pre_tool_use_bash_input)]


def test_cli_pre_tool_use_write_hook(mocker, pre_tool_use_write_input):
    test_list = []

    @hook(Events.PreToolUse.Write)
    def write_hook(input):
        test_list.append(input)

    mocker.patch("sys.stdin.read", return_value=json.dumps(pre_tool_use_write_input))

    _cli()

    assert test_list == [pre_tool_use_write_input]


def test_cli_pre_tool_use_bash_hook_dont_call_other_hooks(
    mocker, pre_tool_use_bash_input
):
    test_list = []

    @hook(Events.PreToolUse.Write)
    def write_hook(input):
        test_list.append(input)

    mocker.patch("sys.stdin.read", return_value=json.dumps(pre_tool_use_bash_input))

    _cli()

    assert test_list == []


def test_multiple_events(mocker, pre_tool_use_bash_input):
    test_list = []

    @hook(Events.PreToolUse.Bash)
    def bash_hook(input):
        test_list.append(("bash_hook", input))

    @hook(Events.PreToolUse.Write)
    def write_hook(input):
        test_list.append(("write_hook", input))

    mocker.patch("sys.stdin.read", return_value=json.dumps(pre_tool_use_bash_input))

    _cli()

    assert test_list == [("bash_hook", pre_tool_use_bash_input)]


def test_multiple_hooks_same_event(mocker, pre_tool_use_bash_input):
    test_list = []

    @hook(Events.PreToolUse.Bash)
    def bash_hook1(input):
        test_list.append(("bash_hook1", input))

    @hook(Events.PreToolUse.Bash)
    def bash_hook2(input):
        test_list.append(("bash_hook2", input))

    mocker.patch("sys.stdin.read", return_value=json.dumps(pre_tool_use_bash_input))

    _cli()

    assert test_list == [
        ("bash_hook1", pre_tool_use_bash_input),
        ("bash_hook2", pre_tool_use_bash_input),
    ]


def test_deny_tool(pre_tool_use_bash_input):
    pre_tool_use_bash_input["tool_input"]["command"] = "BLOCK THIS COMMAND"
    result = call_cli(pre_tool_use_bash_input)
    assert result.returncode == 2
    assert result.stderr.decode() == "Blocking command BLOCK THIS COMMAND\n"
