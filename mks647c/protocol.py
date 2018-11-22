# Copyright (C) 2016, see AUTHORS.md
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

import slave
import logging

import e21_util
from e21_util.lock import InterProcessTransportLock


class MKS647CProtocol:
    def __init__(self, logger=None):

        if logger is None:
            logger = logging.getLogger(__name__)
            logger.addHandler(logging.NullHandler())

        self._logger = logger

    def clear(self, transport):
        with InterProcessTransportLock(transport):
            try:
                while True:
                    transport.read_bytes(5)
            except: # TODO: catch not all exceptions
                return

    def set_logger(self, logger):
        self._logger = logger

    def query(self, transport, header, *data):
        with InterProcessTransportLock(transport):
            message = self.create_message(header, *data)
            self.logger.debug('Query: %s', repr(message))
            with transport:
                transport.write(message)
                response = transport.read_until(self.terminal.encode(self.encoding))
            self._logger.debug('Response: %s', repr(response))
            return self.parse_response(response, header)

    def write(self, transport, header, *data):
        """with InterProcessTransportLock(transport):
            message = self.create_message(header, *data)
            self._logger.debug('Write: %s', repr(message))
            with transport:
                transport.write(message)
        """