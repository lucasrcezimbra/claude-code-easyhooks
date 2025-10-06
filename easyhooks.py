import importlib
import json
import sys
from pathlib import Path

_registered_hooks = {}


def hook(filters):
    def wrapper(func):
        for f in filters:
            _registered_hooks.setdefault(f, [])
            _registered_hooks[f].append(func)

        return func

    return wrapper


class Events:
    # TODO: add others
    class PreToolUse:
        # TODO: add others
        Bash = "Bash"
        Write = "Write"


def _cli():
    path_to_hooks = (
        Path(sys.argv[1])
        if len(sys.argv) > 1
        else (Path.home() / ".claude" / "easyhooks")
    )

    sys.path.insert(0, str(path_to_hooks))

    for file in path_to_hooks.glob("*.py"):
        if file.name != "__init__.py":
            module_name = file.stem
            importlib.import_module(module_name)

    input_data = json.loads(sys.stdin.read())
    # TODO: dataclass

    # TODO: autodiscover hooks
    for event, funcs in _registered_hooks.items():
        # TODO: _registered_hooks.get by hook_event_name and tool_name
        if (
            input_data["hook_event_name"] == "PreToolUse"
            and event == input_data["tool_name"]
        ):
            for f in funcs:
                f(input_data)


__author__ = """Lucas Rangel Cezimbra"""
__email__ = "lucas@cezimbra.tec.br"
__version__ = "0.0.1"

if __name__ == "__main__":
    _cli()
