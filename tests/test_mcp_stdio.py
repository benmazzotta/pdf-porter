"""End-to-end test: launch the installed `pdf-porter` script over stdio.

This mirrors how a desktop app (e.g. Claude Desktop) starts the server: an
absolute command path, a bare environment (only PATH and HOME), and the MCP
SDK's own stdio client. It catches breaks that the in-process tests in
test_server.py cannot see, such as an upstream mcp release changing the
transport or handshake.
"""
import os
import shutil
import sys
from pathlib import Path

import pytest
from mcp import ClientSession, types
from mcp.client.stdio import StdioServerParameters, stdio_client

FIXTURES = Path(__file__).parent / "fixtures"

# Docling loads its models when the server starts, which can take a while on a
# cold cache. Keep the timeout generous so a slow start is not a false alarm.
TIMEOUT_SECONDS = 300

pytestmark = pytest.mark.anyio


@pytest.fixture
def anyio_backend():
    return "asyncio"


def _server_command() -> str:
    # Prefer the script next to the running interpreter (the active venv).
    found = shutil.which("pdf-porter", path=str(Path(sys.executable).parent))
    found = found or shutil.which("pdf-porter")
    assert found, "pdf-porter console script is not installed in this environment"
    return found


def _minimal_env() -> dict[str, str]:
    # Desktop apps launch MCP servers with a sparse environment, not your shell's.
    return {
        "PATH": "/usr/bin:/bin:/usr/sbin:/sbin",
        "HOME": os.environ.get("HOME", str(Path.home())),
    }


async def test_stdio_handshake_list_and_call():
    params = StdioServerParameters(command=_server_command(), env=_minimal_env())

    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write, read_timeout_seconds=TIMEOUT_SECONDS) as session:
            init = await session.initialize()
            assert init.server_info.name == "pdf-porter"

            listed = await session.list_tools()
            tools = {tool.name: tool for tool in listed.tools}
            assert "pdf_to_markdown" in tools
            props = tools["pdf_to_markdown"].input_schema.get("properties", {})
            for arg in ("path", "pdf_base64", "save_output", "output_dir", "filename"):
                assert arg in props, f"pdf_to_markdown is missing argument {arg!r}"

            result = await session.call_tool(
                "pdf_to_markdown", {"path": str(FIXTURES / "simple.pdf")}
            )
            assert isinstance(result, types.CallToolResult)
            assert not result.is_error
            text = "".join(
                block.text for block in result.content if isinstance(block, types.TextContent)
            )
            assert len(text) > 100
            assert not text.startswith("Error:")
