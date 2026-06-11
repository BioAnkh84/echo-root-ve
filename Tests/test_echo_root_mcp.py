from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import sys

REPO = Path(__file__).resolve().parent.parent
MCP_DIR = REPO / ".codex" / "mcp"
sys.path.insert(0, str(MCP_DIR))

import echo_root_mcp  # noqa: E402


class EchoRootMcpTests(unittest.TestCase):
    def test_initialize_returns_tools_capability_and_instructions(self) -> None:
        response = echo_root_mcp.handle_request({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})

        self.assertEqual(response["result"]["serverInfo"]["name"], "echo-root-ve")
        self.assertIn("tools", response["result"]["capabilities"])
        self.assertIn("Presence is not proof", response["result"]["instructions"])

    def test_tools_list_includes_gate_and_receipts(self) -> None:
        response = echo_root_mcp.handle_request({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
        names = {tool["name"] for tool in response["result"]["tools"]}

        self.assertIn("echo_root_gate_action", names)
        self.assertIn("echo_root_append_receipt", names)
        self.assertIn("echo_root_verify_chain", names)

    def test_gate_action_pauses_on_missing_scope(self) -> None:
        response = echo_root_mcp.handle_request(
            {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "echo_root_gate_action",
                    "arguments": {
                        "requested_action": "write release notes",
                        "consent_scope_present": False,
                        "rho": 0.8,
                        "delta": 0.1,
                    },
                },
            }
        )

        data = response["result"]["structuredContent"]
        self.assertEqual(data["decision"], "PAUSE")
        self.assertIn("missing scope", data["reason"])

    def test_repo_map_returns_orientation_boundary(self) -> None:
        response = echo_root_mcp.handle_request(
            {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {"name": "echo_root_repo_map", "arguments": {"depth": 1}},
            }
        )

        data = response["result"]["structuredContent"]
        self.assertEqual(data["receipt_type"], "repo_map")
        self.assertIn("orientation", data["orientation_use"])

    def test_append_receipt_then_verify_chain(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            ledger = str(Path(temp) / "mcp_receipts.jsonl")
            append_response = echo_root_mcp.handle_request(
                {
                    "jsonrpc": "2.0",
                    "id": 5,
                    "method": "tools/call",
                    "params": {
                        "name": "echo_root_append_receipt",
                        "arguments": {
                            "ledger": ledger,
                            "requested_action": "mcp smoke receipt",
                            "consent_scope_present": True,
                            "rho": 0.8,
                            "delta": 0.1,
                            "confidence": "high",
                        },
                    },
                }
            )
            verify_response = echo_root_mcp.handle_request(
                {
                    "jsonrpc": "2.0",
                    "id": 6,
                    "method": "tools/call",
                    "params": {"name": "echo_root_verify_chain", "arguments": {"ledger": ledger}},
                }
            )

            self.assertEqual(append_response["result"]["structuredContent"]["decision"], "PROCEED")
            self.assertTrue(verify_response["result"]["structuredContent"]["ok"])

    def test_response_can_be_encoded_as_json(self) -> None:
        response = echo_root_mcp.handle_request({"jsonrpc": "2.0", "id": 7, "method": "tools/list"})

        json.dumps(response)


if __name__ == "__main__":
    unittest.main()
