from __future__ import annotations

from typing import Any, ClassVar


class Mailbox:
    """Class for keeping track of the shared data between the log readers and
    the channel handlers.

    This implementation tracks the latest converted ADP channel data and the latest
    messages that were read from logs.
    """

    # Hold all the latest messages from the log(s).
    latest_messages: ClassVar[dict[str, Any]] = {}
    # Hold all the latest proto outputs AFTER conversion to ADP.
    latest_outputs: ClassVar[dict[str, Any]] = {}
