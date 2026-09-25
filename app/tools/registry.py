from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class Tool:
    name: str
    handler: Callable
    allowed_roles: frozenset[str]
    sensitive: bool = False


class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, Tool] = {}

    def register(self, name, handler, allowed_roles, sensitive=False):
        if not name or not callable(handler):
            raise ValueError("Tool name and callable handler are required.")
        self._tools[name] = Tool(
            name=name,
            handler=handler,
            allowed_roles=frozenset(allowed_roles),
            sensitive=sensitive,
        )

    def get(self, name):
        if name not in self._tools:
            raise KeyError(f"Unknown tool: {name}")
        return self._tools[name]

    def list(self):
        return sorted(self._tools)

    def authorize(self, role, name):
        tool = self.get(name)
        if role not in tool.allowed_roles:
            raise PermissionError(f"{role} is not authorized to use {name}.")
        return tool
