import json
import subprocess


def test_cli_installed():
    result = subprocess.run(
        ["cc-easyhooks"],
        input=json.dumps({}).encode(),
        capture_output=True,
    )

    assert result.returncode == 0
