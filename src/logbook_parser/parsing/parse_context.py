from typing import Dict

from logbook_parser.util.publisher_consumer import MessagePublisher


class ParseContext:
    def __init__(self, msg_pub: MessagePublisher | None = None) -> None:
        if msg_pub is None:
            self.msg_pub = MessagePublisher(consumers=[])
        else:
            self.msg_pub = msg_pub
        self.extra: Dict = {}
