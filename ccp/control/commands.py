"""Command definitions for deterministic control signals (help, cancel, undo, reset, status)."""

from typing import Dict, Optional

from ccp.config import load_commands
from ccp.control.shortcuts import build_alias_map
from ccp.models import CommandsConfig, ControlResult


class CommandHandler:
    """Intercepts control commands via exact match + aliases.

    Returns a ControlResult if input is a recognized command, otherwise None.
    """

    def __init__(self, config: Optional[CommandsConfig] = None):
        self._config = config or load_commands()
        self._alias_map = build_alias_map(self._config)
        self._descriptions: Dict[str, str] = {
            cmd.name: cmd.description for cmd in self._config.commands
        }

    def try_handle(self, text: str) -> Optional[ControlResult]:
        """Check if text is a control command. Returns ControlResult or None."""
        normalized = text.strip().lower()
        canonical = self._alias_map.get(normalized)
        if canonical is None:
            return None

        handler = getattr(self, f"_handle_{canonical}", None)
        if handler:
            return handler()

        return ControlResult(
            intercepted=True,
            command=canonical,
            message=f"Command '{canonical}' recognized.",
        )

    def _handle_help(self) -> ControlResult:
        lines = ["Available commands:"]
        for cmd in self._config.commands:
            aliases = ", ".join(cmd.aliases) if cmd.aliases else "none"
            lines.append(f"  {cmd.name} ({aliases}) - {cmd.description}")
        return ControlResult(
            intercepted=True,
            command="help",
            message="\n".join(lines),
        )

    def _handle_status(self) -> ControlResult:
        return ControlResult(
            intercepted=True,
            command="status",
            message="Status requested.",
            data={"request": "status"},
        )

    def _handle_confirm(self) -> ControlResult:
        return ControlResult(
            intercepted=True,
            command="confirm",
            message="Confirmation received.",
            data={"confirmation": True},
        )

    def _handle_deny(self) -> ControlResult:
        return ControlResult(
            intercepted=True,
            command="deny",
            message="Denial received.",
            data={"confirmation": False},
        )

    def _handle_cancel(self) -> ControlResult:
        return ControlResult(
            intercepted=True,
            command="cancel",
            message="Operation cancelled.",
        )

    def _handle_undo(self) -> ControlResult:
        return ControlResult(
            intercepted=True,
            command="undo",
            message="Undo requested.",
            data={"request": "undo"},
        )

    def _handle_reset(self) -> ControlResult:
        return ControlResult(
            intercepted=True,
            command="reset",
            message="Session reset requested.",
            data={"request": "reset"},
        )

    def _handle_back(self) -> ControlResult:
        return ControlResult(
            intercepted=True,
            command="back",
            message="Going back to previous state.",
            data={"request": "back"},
        )

    def _handle_escalate(self) -> ControlResult:
        return ControlResult(
            intercepted=True,
            command="escalate",
            message="Escalation requested.",
            data={"request": "escalate"},
        )
