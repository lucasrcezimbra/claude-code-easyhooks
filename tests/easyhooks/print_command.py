from easyhooks import DenyTool, Events, hook


@hook(Events.PreToolUse.Bash)
def print_command(input):
    print("Printing command:", input["tool_input"]["command"])


@hook(Events.PreToolUse.Bash)
def block_command(input):
    cmd = input["tool_input"]["command"]
    if "BLOCK" in cmd:
        raise DenyTool(f"Blocking command {cmd}")
