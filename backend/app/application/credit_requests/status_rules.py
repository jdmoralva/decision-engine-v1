from __future__ import annotations


class InvalidCreditRequestTransitionError(Exception):
    pass


STATUS_ALIASES = {
    "registered": "registrada",
    "in_review": "en_revision",
    "approved": "aprobada",
    "rejected": "rechazada",
    "cancelled": "anulada",
}


def normalize_credit_request_status(value: str) -> str:
    normalized = value.strip().lower()
    return STATUS_ALIASES.get(normalized, normalized)


class CreditRequestStatusRules:
    _allowed_transitions = {
        "registrada": {"en_revision", "anulada"},
        "en_revision": {"aprobada", "rechazada", "anulada"},
        "aprobada": set(),
        "rechazada": set(),
        "anulada": set(),
    }

    def validate_transition(self, *, current_status: str, target_status: str, actor_roles: list[str]) -> str:
        current = normalize_credit_request_status(current_status)
        target = normalize_credit_request_status(target_status)
        allowed = self._allowed_transitions.get(current, set())
        if target not in allowed:
            raise InvalidCreditRequestTransitionError(
                f"The transition '{current} -> {target}' is not allowed."
            )

        if target == "en_revision":
            if not self._has_any_role(actor_roles, {"analista", "evaluador", "admin"}):
                raise InvalidCreditRequestTransitionError(
                    f"The current roles cannot move a request from '{current}' to '{target}'."
                )
            return target

        if target in {"aprobada", "rechazada", "anulada"}:
            if not self._has_any_role(actor_roles, {"evaluador", "admin"}):
                raise InvalidCreditRequestTransitionError(
                    f"The current roles cannot move a request from '{current}' to '{target}'."
                )
            return target

        raise InvalidCreditRequestTransitionError(f"Unsupported target status '{target}'.")

    def available_actions(self, *, current_status: str, actor_roles: list[str]) -> list[str]:
        current = normalize_credit_request_status(current_status)
        actions: list[str] = []
        for candidate in self._allowed_transitions.get(current, set()):
            try:
                validated = self.validate_transition(
                    current_status=current,
                    target_status=candidate,
                    actor_roles=actor_roles,
                )
            except InvalidCreditRequestTransitionError:
                continue
            actions.append(validated)
        return sorted(actions)

    def _has_any_role(self, actor_roles: list[str], expected_roles: set[str]) -> bool:
        return any(role in expected_roles for role in actor_roles)
