from easyhooks import Events, hook


@hook([Events.PreToolUse.Bash])
def print_command(input):
    print("Printing command:", input["tool_input"]["command"])
