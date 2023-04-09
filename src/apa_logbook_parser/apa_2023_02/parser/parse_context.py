from typing import Any


class ParseContext:
    def __init__(self, source: str, extra: dict[str, Any]) -> None:
        self.source = source
        self.extra = extra
