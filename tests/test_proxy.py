import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest

import proxy


class FakeTargetSession:
    async def call_tool(self, name, arguments):
        class Result:
            content = [f"real result for {name}"]
        return Result()


class FakePolicy:
    def __init__(self, decision):
        self.decision = decision

    def decide(self, name):
        return self.decision


@pytest.mark.asyncio
async def test_allow_calls_target(monkeypatch):
    monkeypatch.setattr(proxy, "policy", FakePolicy("allow"))
    monkeypatch.setattr(proxy, "target_session", FakeTargetSession())

    result = await proxy.call_tool("list_notes", {})
    assert result == ["real result for list_notes"]


@pytest.mark.asyncio
async def test_deny_never_calls_target(monkeypatch):
    monkeypatch.setattr(proxy, "policy", FakePolicy("deny"))
    monkeypatch.setattr(proxy, "target_session", FakeTargetSession())

    result = await proxy.call_tool("send_message", {"to": "x", "text": "y"})
    assert "blocked by policy" in result[0].text


@pytest.mark.asyncio
async def test_ask_approved_calls_target(monkeypatch):
    monkeypatch.setattr(proxy, "policy", FakePolicy("ask"))
    monkeypatch.setattr(proxy, "target_session", FakeTargetSession())

    async def fake_ask_human(name, arguments):
        return True

    monkeypatch.setattr(proxy, "ask_human", fake_ask_human)

    result = await proxy.call_tool("delete_note", {"name": "meeting.txt"})
    assert result == ["real result for delete_note"]


@pytest.mark.asyncio
async def test_ask_denied_never_calls_target(monkeypatch):
    monkeypatch.setattr(proxy, "policy", FakePolicy("ask"))
    monkeypatch.setattr(proxy, "target_session", FakeTargetSession())

    async def fake_ask_human(name, arguments):
        return False

    monkeypatch.setattr(proxy, "ask_human", fake_ask_human)

    result = await proxy.call_tool("delete_note", {"name": "meeting.txt"})
    assert "denied by user" in result[0].text