## Project Overview

This is a micro-framework for creating hooks for Claude Code. The framework allows users to intercept and validate tool calls (like Bash, Write, Edit, etc.) before they execute, enabling enforcement of custom policies and best practices.

## Architecture

The core architecture consists of:

- **easyhooks.py**: Single-file framework containing:
  - `hook()` decorator: Registers functions to specific events (e.g., `Events.PreToolUse.Bash`)
  - `Events` class: Defines available hook events for different Claude Code tools
  - `DenyTool` exception: Raised to block a tool call with a custom message
  - `_cli()` function: Entry point that loads user hooks from `~/.claude/easyhooks/` and processes stdin JSON

- **Hook Loading Mechanism**: The CLI dynamically imports all `.py` files from the user's easyhooks directory (`$HOME/.claude/easyhooks/` by default, or a custom path via CLI argument). Hooks are registered via the `@hook()` decorator.

- **Input Format**: Claude Code passes JSON via stdin with structure:
  ```json
  {
    "session_id": "...",
    "hook_event_name": "PreToolUse",
    "tool_name": "Bash",
    "tool_input": {"command": "ls"}
  }
  ```

- **Hook Execution**: Hooks are called in registration order. If `DenyTool` is raised, the CLI exits with code 2 and prints the error to stderr.

## Available Events

All events are under `Events.PreToolUse`:
- `Bash`, `Edit`, `Glob`, `Grep`, `MultiEdit`, `Read`, `Task`, `WebFetch`, `WebSearch`, `Write`

## Development Commands

### Setup
```bash
make install
```
Installs dependencies with Poetry and sets up pre-commit hooks.

### Testing
```bash
make test                 # Run all tests
make test-cov            # Run tests with coverage for easyhooks module
poetry run pytest        # Direct pytest invocation
```

Test files can match: `tests.py`, `test_*.py`, `*_tests.py`

### Linting
```bash
make lint
```
Runs pre-commit hooks on all files and checks for dead pytest fixtures.

### Building
```bash
make build
```
Builds the package using Poetry.

### Template Updates
```bash
make update-template
```
Updates project structure from cookiecutter template using cruft.

## CLI Entry Points

The package provides 4 CLI aliases (all equivalent):
- `claude-code-easyhooks`
- `cc-easyhooks`
- `easyhooks`
- `cceh`

## Testing Strategy

Tests are in `tests/test_cli.py` and verify:
- Hook registration and execution
- Multiple hooks on same event
- Event filtering (hooks only fire for their registered events)
- `DenyTool` exception handling (exit code 2)
- Custom easyhooks directory loading

Test fixtures mock stdin to simulate Claude Code's JSON input.

## Key Implementation Details

- The framework uses a global `_registered_hooks` dict to map event names to lists of hook functions
- Hook functions receive the full input dict and can inspect/validate tool parameters
- No external dependencies required (pure Python stdlib)
- Supports Python 3.9+
