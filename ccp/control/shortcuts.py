"""Fast-path resolution for control signals — keyword and pattern matching for commands."""

from typing import Dict

from ccp.models import CommandsConfig


def build_alias_map(config: CommandsConfig) -> Dict[str, str]:
    """Build a lookup dict mapping each alias (and canonical name) to the canonical command name.

    Returns:
        Dict mapping lowercase string -> canonical command name.
        E.g. {"help": "help", "?": "help", "h": "help", "cancel": "cancel", ...}
    """
    alias_map: Dict[str, str] = {}
    for cmd in config.commands:
        canonical = cmd.name.lower()
        alias_map[canonical] = canonical
        for alias in cmd.aliases:
            alias_map[alias.lower()] = canonical
    return alias_map
