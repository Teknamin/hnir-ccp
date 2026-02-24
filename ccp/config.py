"""YAML config loader for policies, states, and commands."""

from pathlib import Path
from typing import Union

import yaml

from ccp.models import CommandsConfig, PolicyConfig, StatesConfig

_CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"


def _load_yaml(filename: str, config_dir: Union[Path, None] = None) -> dict:
    """Load a YAML file from the config directory."""
    path = (config_dir or _CONFIG_DIR) / filename
    with open(path, "r") as f:
        return yaml.safe_load(f)


def load_policies(config_dir: Union[Path, None] = None) -> PolicyConfig:
    """Load and validate policy rules from policies.yaml."""
    data = _load_yaml("policies.yaml", config_dir)
    return PolicyConfig(**data)


def load_states(config_dir: Union[Path, None] = None) -> StatesConfig:
    """Load and validate state definitions from states.yaml."""
    data = _load_yaml("states.yaml", config_dir)
    return StatesConfig(**data)


def load_commands(config_dir: Union[Path, None] = None) -> CommandsConfig:
    """Load and validate command definitions from commands.yaml."""
    data = _load_yaml("commands.yaml", config_dir)
    return CommandsConfig(**data)
