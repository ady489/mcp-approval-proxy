import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from policy import Policy


def write_policy(tmp_path, content):
    path = tmp_path / "policy.yaml"
    path.write_text(content)
    return str(path)


def test_allow_rule(tmp_path):
    path = write_policy(tmp_path, "default: ask\nrules:\n  list_notes: allow\n")
    policy = Policy(path)
    assert policy.decide("list_notes") == "allow"


def test_deny_rule(tmp_path):
    path = write_policy(tmp_path, "default: ask\nrules:\n  send_message: deny\n")
    policy = Policy(path)
    assert policy.decide("send_message") == "deny"


def test_unknown_tool_falls_back_to_default(tmp_path):
    path = write_policy(tmp_path, "default: ask\nrules:\n  list_notes: allow\n")
    policy = Policy(path)
    assert policy.decide("some_new_tool") == "ask"


def test_default_can_be_allow(tmp_path):
    path = write_policy(tmp_path, "default: allow\nrules: {}\n")
    policy = Policy(path)
    assert policy.decide("anything") == "allow"