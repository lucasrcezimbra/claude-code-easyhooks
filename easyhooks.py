import json
import sys

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
