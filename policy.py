from pathlib import Path

import yaml


class Policy:
    def __init__(self, path: str):
        data = yaml.safe_load(Path(path).read_text())
        self.default = data.get("default", "ask")
        self.rules = data.get("rules", {})

    def decide(self, tool_name: str) -> str:
        return self.rules.get(tool_name, self.default)