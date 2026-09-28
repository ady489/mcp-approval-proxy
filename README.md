# mcp-approval-proxy

A proxy that sits between an AI agent and a real MCP server, and pauses for human approval before risky tool calls go through.

## Why

Agents built on top of MCP can call tools that delete files, send messages, or otherwise act in the real world. Most demos either trust the agent completely or bake a single approval step into one specific agent. This proxy is a general-purpose layer: any MCP client can connect to it instead of connecting directly to a server, and a policy file decides, per tool, whether a call is allowed automatically, needs a human to approve it, or is blocked outright.

I built this after working through the agentic AI course's Sidekick lab, which has a human-in-the-loop approval step built into one agent. I wanted to see if the same idea could work as a general layer in front of *any* MCP server, independent of the agent using it.

## How it works
client (agent) <--MCP--> proxy.py <--MCP--> demo_server.py (real tools)
|
policy.yaml
|
approvals/ (file queue) <--> approve.py (human)

- `demo_server.py` is a small MCP server with four tools over a sandbox folder: `list_notes`, `read_note`, `delete_note`, `send_message` (a stand-in for anything real that shouldn't fire without a human okaying it).
- `proxy.py` is itself an MCP server to the client, but forwards every call to the real target server. Before forwarding, it checks `policy.yaml`.
- `policy.yaml` maps each tool name to `allow`, `ask`, or `deny`, with a configurable default for unlisted tools.
- When a tool needs approval, the proxy writes a request file to `approvals/` and waits (without blocking anything else) for a response file to appear.
- `approve.py` runs in its own terminal, watches that folder, asks a human, and writes the response.

## Running it

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# recreate the sandbox files (not committed, since delete_note removes them during testing)
mkdir -p sandbox
echo "buy milk" > sandbox/todo.txt
echo "meeting at 10" > sandbox/meeting.txt
```

In one terminal:
```bash
python approve.py
```

In another:
```bash
python try_client.py
```

`try_client.py` calls all four tools through the proxy. `list_notes` and `read_note` are set to `allow` and run immediately. `delete_note` is set to `ask`, so it pauses until you approve it in the `approve.py` terminal. `send_message` is set to `deny`, so it's blocked before it ever reaches the real server.

Run the automated tests with:
```bash
python -m pytest
```
(Use `python -m pytest` rather than plain `pytest` — see note below.)

## Policy format

```yaml
default: ask

rules:
  list_notes: allow
  read_note: allow
  delete_note: ask
  send_message: deny
```

Any tool not listed falls back to `default`.

## Things I ran into while building this

- **Output schema validation error.** FastMCP infers a structured-output schema from a tool's return type annotation, and validation fails if the tool doesn't actually return structured content. Fixed by dropping return-type annotations on the demo server's tools, so it falls back to plain text content.
- **`/dev/tty` isn't reliable for approval prompts.** My first approach had the proxy call Python's `input()` directly, but the proxy's stdin/stdout are wired to the MCP protocol, not a keyboard, so this corrupted the JSON-RPC stream. Switching to reading/writing `/dev/tty` directly hit `[Errno 6] Device not configured`, since the proxy process, spawned as a subprocess, doesn't reliably have a controlling terminal. This also isn't realistic anyway — real MCP servers are usually launched silently by tools like Claude Desktop with no terminal at all. I redesigned it as a file-based request/response queue instead, which works regardless of how the proxy was launched, and sets up cleanly for a future Telegram-based approval channel.
- **`pytest` picked up the wrong Python.** With both conda's `base` environment and a project `.venv` active, plain `pytest` ran from conda's site-packages instead of the virtualenv, and couldn't find the project's dependencies. Running `python -m pytest` fixes this by using whichever `python` is currently active.

## Limitations / possible extensions

- Policy decisions are based on tool name only, not on the actual arguments (e.g. `delete_note` always asks, rather than only asking when the file matches something important).
- The approval queue is polled with `asyncio.sleep`, not event-driven.
- Approval currently only works through a terminal running `approve.py`. A Telegram bot or web UI would make this usable when you're not at your computer.


https://github.com/user-attachments/assets/ccddb436-7767-4882-9cda-130592092c23





