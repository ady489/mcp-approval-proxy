from pathlib import Path
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("demo-notes")

NOTES = Path(__file__).parent / "sandbox"


@mcp.tool()
def list_notes():
    """List the notes in the sandbox folder."""
    names = sorted(p.name for p in NOTES.glob("*.txt"))
    return "\n".join(names)


@mcp.tool()
def read_note(name: str):
    """Read a note by file name."""
    return (NOTES / Path(name).name).read_text()


@mcp.tool()
def delete_note(name: str):
    """Delete a note by file name."""
    (NOTES / Path(name).name).unlink()
    return f"deleted {name}"


@mcp.tool()
def send_message(to: str, text: str):
    """Pretend to send a message."""
    return f"message sent to {to}"


if __name__ == "__main__":
    mcp.run()