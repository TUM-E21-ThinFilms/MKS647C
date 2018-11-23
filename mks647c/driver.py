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

from mks647c.protocol import MKS647CProtocol
from e21_util.pvd.transport import Serial

class MKS647CDriver:

    def __init__(self, transport: Serial, protocol: MKS647CProtocol=None):

        self._transport = transport

        if protocol is None:
            protocol = MKS647CProtocol()

        self._protocol = protocol

    def test(self):
        self._transport.write("GM 0 " + chr(0x0d) + chr(0x0a))

        print(self._transport.read(1000))



