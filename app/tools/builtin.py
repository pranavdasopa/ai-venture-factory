from datetime import datetime, timezone


def runtime_health(**_):
    return {
        "ok": True,
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "service": "company-core",
    }


def register_builtin_tools(registry):
    registry.register(
        "system.runtime_health",
        runtime_health,
        allowed_roles=frozenset({
            "CEO", "CTO", "COO", "SECURITY", "QA", "CRITIC"
        }),
        sensitive=False,
    )
