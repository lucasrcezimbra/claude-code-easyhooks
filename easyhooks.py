import importlib
import json
import logging
import sys
from pathlib import Path

# TODO: log to file
logger = logging.getLogger(__name__)

_registered_hooks = {}


def hook(*filters):
    def wrapper(func):
        for f in filters:
            logging.debug(f"Registering hook {func} for filter {f}")
            _registered_hooks.setdefault(f, [])
            _registered_hooks[f].append(func)

        return func

    return wrapper


class Events:
    # TODO: add others
    class PreToolUse:
        Bash = "PreToolUse.Bash"
        Edit = "PreToolUse.Edit"
        Glob = "PreToolUse.Glob"
        Grep = "PreToolUse.Grep"
        MultiEdit = "PreToolUse.MultiEdit"
        Read = "PreToolUse.Read"
        Task = "PreToolUse.Task"
        WebFetch = "PreToolUse.WebFetch"
        WebSearch = "PreToolUse.WebSearch"
        Write = "PreToolUse.Write"


class DenyTool(Exception):
    pass


def _cli():
    path_to_hooks = (
        Path(sys.argv[1])
        if len(sys.argv) > 1
        else (Path.home() / ".claude" / "easyhooks")
    )

    logger.info(f"Loading hooks from {path_to_hooks}")

    sys.path.insert(0, str(path_to_hooks))

    for file in path_to_hooks.glob("*.py"):
        if file.name != "__init__.py":
            module_name = file.stem
            logger.info(f"Loading hook {module_name}")
            importlib.import_module(module_name)

    input_data = json.loads(sys.stdin.read())
    logger.debug(input_data)
    # TODO: dataclass

    # TODO: extract this logic
    funcs = _registered_hooks.get(
        f'{input_data["hook_event_name"]}.{input_data["tool_name"]}', []
    )
    try:
        for f in funcs:
            logger.info(f"Calling hook {f}")
            f(input_data)
    except DenyTool as e:
        print(str(e), file=sys.stderr)
        sys.exit(2)


__author__ = """Lucas Rangel Cezimbra"""
__email__ = "lucas@cezimbra.tec.br"
__version__ = "0.0.1"

if __name__ == "__main__":
    _cli()
