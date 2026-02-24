"""Role and permission checks for action authorization."""

from typing import Set


def check_authorization(user_roles: Set[str], required_roles: Set[str]) -> bool:
    """Check if user has at least one of the required roles.

    If required_roles is empty, authorization is granted (no restriction).
    """
    if not required_roles:
        return True
    return bool(user_roles & required_roles)
