"""Tests for ccp.control."""

from ccp.config import load_commands
from ccp.control.commands import CommandHandler
from ccp.control.shortcuts import build_alias_map


def test_build_alias_map():
    config = load_commands()
    alias_map = build_alias_map(config)
    assert alias_map["help"] == "help"
    assert alias_map["?"] == "help"
    assert alias_map["h"] == "help"
    assert alias_map["confirm"] == "confirm"
    assert alias_map["yes"] == "confirm"
    assert alias_map["y"] == "confirm"


def test_command_handler_recognized():
    handler = CommandHandler()
    result = handler.try_handle("help")
    assert result is not None
    assert result.intercepted is True
    assert result.command == "help"


def test_command_handler_alias():
    handler = CommandHandler()
    result = handler.try_handle("?")
    assert result is not None
    assert result.command == "help"


def test_command_handler_case_insensitive():
    handler = CommandHandler()
    result = handler.try_handle("HELP")
    assert result is not None
    assert result.command == "help"


def test_command_handler_not_recognized():
    handler = CommandHandler()
    result = handler.try_handle("random text")
    assert result is None


def test_command_handler_confirm():
    handler = CommandHandler()
    result = handler.try_handle("confirm")
    assert result.command == "confirm"
    assert result.data["confirmation"] is True


def test_command_handler_deny():
    handler = CommandHandler()
    result = handler.try_handle("deny")
    assert result.command == "deny"
    assert result.data["confirmation"] is False


def test_command_handler_status():
    handler = CommandHandler()
    result = handler.try_handle("status")
    assert result.command == "status"


def test_command_handler_all_commands():
    handler = CommandHandler()
    commands = ["help", "cancel", "undo", "reset", "status", "back", "confirm", "deny", "escalate"]
    for cmd in commands:
        result = handler.try_handle(cmd)
        assert result is not None, f"Command '{cmd}' not handled"
        assert result.intercepted is True
        assert result.command == cmd


def test_help_message_content():
    handler = CommandHandler()
    result = handler.try_handle("help")
    assert "Available commands:" in result.message
    assert "help" in result.message
    assert "confirm" in result.message
