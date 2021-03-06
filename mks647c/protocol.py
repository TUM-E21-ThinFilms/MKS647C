# Copyright (C) 2018, see AUTHORS.md
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging

import e21_util
from e21_util.lock import InterProcessTransportLock
from mks647c.message import AbstractMessage, GrammarChannelMessage, GrammarGeneralResponse
from mks647c.message import GrammarChannelMessage


class ResponseError(RuntimeError):
    pass

class MKS647CProtocol:
    def __init__(self, logger=None):

        if logger is None:
            logger = logging.getLogger(__name__)
            logger.addHandler(logging.NullHandler())

        self._logger = logger

    def clear(self, transport):
        with InterProcessTransportLock(transport):  # lock and then unlock afterwards
            try:
                while True:
                    transport.read_bytes(10)
            except:
                return

    def create_message(self, msg: AbstractMessage):
        raw_msg = msg.generate()
        return raw_msg

    def set_logger(self, logger):
        self._logger = logger

    def parse_response(self, raw_response, cls):
        try:
            response = cls().parse(raw_response)
        except:
            # TODO: ALEX: do not catch all exceptions, only exceptions from parsing.
            raise ResponseError("Could not parse message")

        if response.has_error():
            if response.get_error_code() == 0:
                raise ResponseError("Channel error: No Channel or unknown channel was specified")
            if response.get_error_code() == 1:
                raise ResponseError("An unknown command was transmitted")
            if response.get_error_code() == 2:
                raise ResponseError("Syntax error, invalid command length")
            if response.get_error_code() == 3:
                raise ResponseError("Invalid expression given in message")
            if response.get_error_code() == 4:
                raise ResponseError("Invalid value given in message")
            if response.get_error_code() == 5:
                raise ResponseError("Autozero error. Channel was not switched off?")

            raise ResponseError("Received an unknown error from the device")

    def read_response(self, transport, msg: AbstractMessage):
        response = transport.read_until(bytes(GrammarChannelMessage.TOKEN_NL, 'ascii'))
        self._logger.debug('Response: %s', repr(response))
        return self.parse_response(response.decode('ascii') + "\n", msg.get_response_class())

    def query(self, transport, msg: AbstractMessage):
        with InterProcessTransportLock(transport):
            raw_str_msg = self.create_message(msg)
            self._logger.debug('Query: %s', repr(raw_str_msg))
            transport.write(raw_str_msg)
            return self.read_response(transport, msg)

    def write(self, transport, msg: AbstractMessage):
        with InterProcessTransportLock(transport):
            raw_str_msg = self.create_message(msg)
            self._logger.debug('Write: %s', repr(raw_str_msg))
            transport.write(raw_str_msg)
            return self.read_response(transport, msg)
