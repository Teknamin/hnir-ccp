"""Action classification and policy evaluation — returns ALLOW, DENY, or CONFIRM decisions."""

from typing import Optional

from ccp.models import (
    ActionType,
    ConversationState,
    GateDecision,
    PolicyResult,
)
from ccp.policy.authorization import check_authorization
from ccp.policy.rules import PolicyRuleSet
from ccp import reason_codes as rc

from typing import Set


class PolicyGate:
    """Evaluates proposed actions against policy rules.

    Evaluation order:
    1. Find matching rule for action type
    2. Check if action is denied outright by rule
    3. Check state deny list
    4. Check authorization (user roles)
    5. Check if confirmation is required
    6. Return ALLOW if all checks pass
    """

    def __init__(self, rule_set: Optional[PolicyRuleSet] = None):
        self._rule_set = rule_set or PolicyRuleSet()

    def evaluate(
        self,
        action_type: ActionType,
        current_state: ConversationState,
        user_roles: Set[str],
        confirmed: bool = False,
    ) -> PolicyResult:
        """Evaluate a proposed action against policy rules."""
        rule = self._rule_set.find_rule(action_type)

        if rule is None:
            return PolicyResult(
                decision=GateDecision.DENY,
                reason=f"No policy rule for action type {action_type.value}",
                reason_code=rc.policy_no_rule(action_type.value),
            )

        # Rule says DENY outright
        if rule.decision == GateDecision.DENY:
            return PolicyResult(
                decision=GateDecision.DENY,
                reason=rule.description or f"Policy denies {action_type.value}",
                reason_code=rc.policy_denied(rule.name),
                rule_name=rule.name,
            )

        # Check state deny list
        if current_state in rule.denied_states:
            return PolicyResult(
                decision=GateDecision.DENY,
                reason=f"{action_type.value} denied in state {current_state.value}",
                reason_code=rc.policy_denied_state(rule.name, current_state.value),
                rule_name=rule.name,
            )

        # Check authorization
        if not check_authorization(user_roles, rule.required_roles):
            roles_str = ",".join(sorted(rule.required_roles))
            return PolicyResult(
                decision=GateDecision.DENY,
                reason=f"Insufficient roles. Needs: {roles_str}",
                reason_code=rc.policy_auth_insufficient(roles_str),
                rule_name=rule.name,
                required_roles=rule.required_roles,
            )

        # Check confirmation requirement
        if rule.require_confirmation and not confirmed:
            return PolicyResult(
                decision=GateDecision.REQUIRE_CONFIRMATION,
                reason=f"{action_type.value} requires confirmation",
                reason_code=rc.policy_confirmation_required(rule.name),
                rule_name=rule.name,
            )

        return PolicyResult(
            decision=GateDecision.ALLOW,
            reason=f"{action_type.value} allowed by rule '{rule.name}'",
            reason_code=rc.policy_allowed(rule.name),
            rule_name=rule.name,
        )
