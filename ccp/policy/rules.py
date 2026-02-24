"""Policy rule definitions — loaded from YAML configuration."""

from typing import List, Optional

from ccp.config import load_policies
from ccp.models import ActionType, PolicyConfig, PolicyRule


class PolicyRuleSet:
    """Loads and provides lookup for policy rules."""

    def __init__(self, config: Optional[PolicyConfig] = None):
        self._config = config or load_policies()
        self._rules_by_type = {}
        for rule in self._config.rules:
            self._rules_by_type[rule.action_type] = rule

    def find_rule(self, action_type: ActionType) -> Optional[PolicyRule]:
        """Find the policy rule for a given action type."""
        return self._rules_by_type.get(action_type)

    @property
    def rules(self) -> List[PolicyRule]:
        """Return all rules."""
        return self._config.rules
