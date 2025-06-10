from __future__ import annotations

import abc
import mailbox
import typing

import data_sender


class ChannelHandlerBase(abc.ABC):
    """
    This channel handler converts the raw data from the log into the ADP format.
    """

    def __init__(self, data_sender: data_sender.DataSender, mailbox: mailbox.Mailbox) -> None:
        raise NotImplementedError()

    def update(self) -> None:
        raise NotImplementedError()

    def get(self) -> typing.Any:
        raise NotImplementedError()
