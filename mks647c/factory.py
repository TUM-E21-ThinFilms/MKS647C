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

from mks647c.protocol import MKS647CProtocol
from mks647c.driver import MKS647CDriver
from e21_util.pvd.transport import Serial
from e21_util.pvd.log import get_pvd_logger
from e21_util.pvd.ports import Ports


class MKS647CFactory:
    def get_logger(self):
        return get_pvd_logger('MKS 647C Mass flow controller', 'mks647c.log')

    def create_device(self, device=None, logger=None):
        if logger is None:
            logger = self.get_logger()

        if device is None:
            device = Ports().get_port(Ports.DEVICE_MKS_GAS_FLOW)

        protocol = MKS647CProtocol(logger=logger)
        return MKS647CDriver(Serial(device, 9600, 8, 'O', 1, 1), protocol)
