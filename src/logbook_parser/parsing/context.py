from typing import Dict


class Context:
    # def __init__(self, msg_pub: MessagePublisher | None = None) -> None:
    #     if msg_pub is None:
    #         self.msg_pub = MessagePublisher(consumers=[])
    #     else:
    #         self.msg_pub = msg_pub
    #     self.extra: Dict = {}
    def __init__(self) -> None:
        self.extra: Dict = {}
