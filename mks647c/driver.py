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
from mks647c.message import GrammarChannelMessage, DataChannelMessage, GrammarIntegerResponse, DataGeneralResponse

from e21_util.pvd.transport import Serial


class InvalidArgumentError(RuntimeError):
    pass


class MKS647CDriver:
    # TODO: ALEX: Folgende cmds folgenden nicht der grammatik:
    #
    # Check-CMD(s) ohne R:
    #   Done: FL c: check for actual flow of a channel
    #   Done: PR: check for pressure
    #   Done: PC: check for PCS (pressure control signal)
    #   Done: AZ c: zero adjust MFC, aber man bekommt ein Offset-Wert zurück
    #   Done: PZ: zero adjust pressure, aber man bekommt ein Offset-Wert zurück
    #   Done: ST c: check for status of a channel
    #   Done: ID: check for identification
    #
    # CMD(s) mit R und Parameters geleichzeitig:
    # GP c s R: check for setpoint in gas set, wofür man auch s=gas_set eingeben muss
    #
    # CMD(s) wo die Channels auch null sein darf:
    #   Done: ON c: open valve, wo c=0 entspricht ON ALL
    #   Done: OF c: close valve, wo c=0 entspricht OFF ALL
    #
    #
    CMD_ZERO_ADJUST = 'AZ'
    CMD_ZERO_ADJUST_PRESSURE = 'PZ'
    CMD_GAS_MENU = 'GM'
    CMD_SETPOINT = 'FS'
    CMD_FLOW = 'FL'
    CMD_PRESSURE = 'PS'
    CMD_PRESSURE_SIGNAL = 'PC'
    CMD_PRESSURE_MODE = 'PM'
    CMD_RANGE = 'RA'
    CMD_GAS_CORRECTION_FACTOR = 'GC'
    CMD_MODE = 'MO'
    CMD_HIGH_LIMIT = 'HL'
    CMD_LOW_LIMIT = 'LL'
    CMD_TRIPLE_LIMIT = 'TM'
    CMD_GAS_SET = 'GP'
    CMD_STATUS = 'ST'
    CMD_IDENTIFICATION = 'ID'
    CMD_OPEN = 'ON'
    CMD_CLOSE = 'OF'

    SETPOINT_MIN = 0
    SETPOINT_MAX = 1100

    CHANNEL_ALL = 0
    CHANNEL_MIN = 1
    CHANNEL_MAX = 8

    GAS_RANGE_MIN = 0
    GAS_RANGE_MAX = 39

    COREECTION_FACTOR_MIN = 10
    COREECTION_FACTOR_MAX = 180

    GAS_MENU_1 = 1
    GAS_MENU_2 = 2
    GAS_MENU_3 = 3
    GAS_MENU_4 = 4
    GAS_MENU_5 = 5
    GAS_MENU_DEFAULT = 0

    GAS_MENUS = [GAS_MENU_1, GAS_MENU_2, GAS_MENU_3, GAS_MENU_4, GAS_MENU_5, GAS_MENU_DEFAULT]

    PRESSURE_MODE_OFF = 0
    PRESSURE_MODE_AUTO = 1

    PRESSURE_MODES = [PRESSURE_MODE_OFF, PRESSURE_MODE_AUTO]

    GAS_RANGE_1_SCCM = 0
    GAS_RANGE_2_SCCM = 1
    GAS_RANGE_5_SCCM = 2
    GAS_RANGE_10_SCCM = 3
    GAS_RANGE_20_SCCM = 4
    GAS_RANGE_50_SCCM = 5
    GAS_RANGE_100_SCCM = 6
    GAS_RANGE_200_SCCM = 7
    GAS_RANGE_500_SCCM = 8

    GAS_RANGE_1_SLM = 9
    GAS_RANGE_2_SLM = 10
    GAS_RANGE_5_SLM = 11
    GAS_RANGE_10_SLM = 12
    GAS_RANGE_20_SLM = 13
    GAS_RANGE_50_SLM = 14
    GAS_RANGE_100_SLM = 15
    GAS_RANGE_200_SLM = 16
    GAS_RANGE_400_SLM = 17
    GAS_RANGE_500_SLM = 18
    GAS_RANGE_30_SLM = 38
    GAS_RANGE_300_SLM = 39

    GAS_RANGE_1_SCMM = 19

    GAS_RANGE_1_SCFH = 20
    GAS_RANGE_2_SCFH = 21
    GAS_RANGE_5_SCFH = 22
    GAS_RANGE_10_SCFH = 23
    GAS_RANGE_20_SCFH = 24
    GAS_RANGE_50_SCFH = 25
    GAS_RANGE_100_SCFH = 26
    GAS_RANGE_200_SCFH = 27
    GAS_RANGE_500_SCFH = 28

    GAS_RANGE_1_SCFM = 29
    GAS_RANGE_2_SCFM = 30
    GAS_RANGE_5_SCFM = 31
    GAS_RANGE_10_SCFM = 32
    GAS_RANGE_20_SCFM = 33
    GAS_RANGE_50_SCFM = 34
    GAS_RANGE_100_SCFM = 35
    GAS_RANGE_200_SCFM = 36
    GAS_RANGE_500_SCFM = 37
    MAX_GAS_RANGE_ID = 39

    CHANNEL_MODE_INDEPENDENT = 0
    CHANNEL_MODE_SLAVE = 1
    CHANNEL_MODE_EXTERN = 2
    CHANNEL_MODE_PCS = 3
    CHANNEL_MODE_TEST = 9

    TRIP_LIMIT_MODE_SLEEP = 0
    TRIP_LIMIT_MODE_LIMIT = 1
    TRIP_LIMIT_MODE_BAND = 2

    TRIP_LIMIT_MODES = [TRIP_LIMIT_MODE_SLEEP, TRIP_LIMIT_MODE_LIMIT, TRIP_LIMIT_MODE_BAND]

    STATUS_BIT_ON_OFF = 0
    STATUS_BIT_TRIP_LIMIT_LOW = 4
    STATUS_BIT_TRIP_LIMIT_HIGH = 5
    STATUS_BIT_OVERFLOW_IN = 6
    STATUS_BIT_UNDERFLOW_IN = 7
    STATUS_BIT_OVERFLOW_OUT = 8
    STATUS_BIT_UNDERFLOW_OUT = 9

    STATUS_BITS = [STATUS_BIT_ON_OFF, STATUS_BIT_TRIP_LIMIT_LOW, STATUS_BIT_TRIP_LIMIT_HIGH, STATUS_BIT_OVERFLOW_IN,
                   STATUS_BIT_UNDERFLOW_IN, STATUS_BIT_OVERFLOW_OUT, STATUS_BIT_UNDERFLOW_OUT]

    def __init__(self, transport: Serial, protocol: MKS647CProtocol = None):

        self._transport = transport

        if protocol is None:
            protocol = MKS647CProtocol()

        self._protocol = protocol

    def _build_msg(self, cmd, channel=None, p1=None, p2=None, p3=None, is_query=True, enable_query_token=None):
        # works also for cmds that do not need any channel
        # 'R' for request, however, is incompatible with parameters p1..p3
        # TODO: adjust it for the cmd 'GP' or write a new method for it (also the syntax class etc)

        msg = GrammarChannelMessage()
        data = DataChannelMessage()

        data.set_command(cmd)

        # Sometimes we have to omit the "R" token
        if enable_query_token is not None:
            data.set_optional_query(enable_query_token)

        # since channel can also be optional
        if channel is not None:
            data.set_channel(channel)

        # if it is to "set": parameters have to be given
        # if it is to "get": is_query = True
        if is_query is True:
            data.set_query()
        else:
            data.set_write()
            data.set_parameter_1(p1)
            data.set_parameter_2(p2)
            data.set_parameter_3(p3)

        msg.set_data(data)
        return msg

    def _write_message(self, syntax):
        return self._protocol.write(self._transport, syntax)

    def _query_message(self, syntax):
        return self._protocol.query(self._transport, syntax)

    def _check_data_existing(self, data: DataGeneralResponse):
        if not data.has_data():
            raise RuntimeError("Did not receive data from the device")

    def _check(self, channel=None, raw_setpoint=None, channel_all_allowed=False):
        if raw_setpoint is not None:
            if raw_setpoint not in range(self.SETPOINT_MIN, self.SETPOINT_MAX + 1):
                raise RuntimeError("Given setpoint %s invalid." % str(raw_setpoint))

        if channel is not None:
            # Warning if refactoring: do not forget to consider this case too!
            if channel_all_allowed is True:
                if channel is self.CHANNEL_ALL:
                    return

            if channel not in range(self.CHANNEL_MIN, self.CHANNEL_MAX + 1):
                raise RuntimeError("Given channel %s invalid." % str(channel))


    def _get_cmd(self, cmd, channel=None, enable_query_token=None):
        # works only for cmds for reading but without extra parameters p1..p3

        self._check(channel=channel)
        msg = self._build_msg(cmd, channel=channel, is_query=True, enable_query_token=enable_query_token)
        msg.set_response_class(GrammarIntegerResponse)
        response = self._query_message(msg)
        self._check_data_existing(response)
        return response

    def _set_cmd(self, cmd, channel=None, p1=None, p2=None, setpoint_percentage=None, channel_all_allowed=False):
        # practically no p3 will be transferred according to the manual
        if setpoint_percentage is not None:
            raw_setpoint = self._to_raw_setpoint(setpoint_percentage)
            self._check(raw_setpoint=raw_setpoint)
            if p1 is not None:
                p2 = raw_setpoint
            else:
                p1 = raw_setpoint
        self._check(channel=channel, channel_all_allowed=channel_all_allowed)
        msg = self._build_msg(cmd, channel=channel, p1=p1, p2=p2, is_query=False)
        return self._write_message(msg)

    @staticmethod
    def _to_raw_setpoint(setpoint_percentage):
        return round(float(setpoint_percentage) * 1000.0)  # from float (0, 1.1) to integer (0, 1100)

    @staticmethod
    def _from_raw_setpoint(setpoint_raw):
        return float(setpoint_raw) / 1000.0  # from integer (0, 1100) to float (0, 1.1)

    @staticmethod
    def _to_raw_correction_factor(correction_factor_percentage):
        return round(float(correction_factor_percentage) * 100.0)  # from float (0.1, 1.8) to integer (10, 180)

    @staticmethod
    def _from_raw_correction_factor(correction_factor_raw):
        return float(correction_factor_raw) / 100.0  # from integer (10, 180) to float (0.1, 1.8)

    def set_gas_menu(self, gas_menu):
        if gas_menu not in self.GAS_MENUS:
            raise InvalidArgumentError("Invalid gas menu given")
        self._set_cmd(self.CMD_GAS_MENU, p1=gas_menu)

    def get_gas_menu(self):
        return int(self._get_cmd(self.CMD_GAS_MENU).get_value_1())

    def set_setpoint(self, channel, setpoint_percentage):
        self._set_cmd(self.CMD_SETPOINT, channel, setpoint_percentage=setpoint_percentage)

    def get_setpoint(self, channel):
        return self._from_raw_setpoint(self._get_cmd(self.CMD_SETPOINT, channel).get_value_1())

    def get_flow(self, channel):
        return self._from_raw_setpoint(self._get_cmd(self.CMD_FLOW, channel, enable_query_token=False).get_value_1())

    def set_pressure(self, setpoint_percentage):
        self._set_cmd(self.CMD_PRESSURE, setpoint_percentage=setpoint_percentage)

    def get_pressure_setpoint(self):
        return self._from_raw_setpoint(self._get_cmd(self.CMD_PRESSURE).get_value_1())

    def get_pressure(self):
        return self._from_raw_setpoint(self._get_cmd(self.CMD_PRESSURE, enable_query_token=False).get_value_1())

    def get_pressure_control_signal(self):
        return self._from_raw_setpoint(self._get_cmd(self.CMD_PRESSURE_SIGNAL, enable_query_token=False).get_value_1())

    def set_pressure_mode(self, mode):
        if mode not in self.PRESSURE_MODES:
            raise RuntimeError("Given pressure mode '{}' is invalid".format(mode))
        self._set_cmd(self.CMD_PRESSURE_MODE, p1=mode)

    def get_pressure_mode(self):
        return int(self._get_cmd(self.CMD_PRESSURE_MODE).get_value_1())

    def set_range(self, channel, range_code):
        if range_code not in range(0, self.MAX_GAS_RANGE_ID + 1):
            raise RuntimeError("Given range code is invalid")
        self._set_cmd(self.CMD_RANGE, channel=channel, p1=range_code)

    def get_range(self, channel):
        return int(self._get_cmd(self.CMD_RANGE, channel=channel).get_value_1())

    def set_gas_correction_factor(self, channel, factor_percentage):
        if not (0.1 <= factor_percentage <= 1.8):
            raise RuntimeError("Given gas correction factor '{}' must be in range [0.1, 1.8]".format(factor_percentage))

        self._set_cmd(self.CMD_GAS_CORRECTION_FACTOR, channel=channel,
                      p1=self._to_raw_correction_factor(factor_percentage))

    def get_gas_correction_factor(self, channel):
        return self._from_raw_correction_factor(self._get_cmd(self.CMD_GAS_CORRECTION_FACTOR, channel).get_value_1())

    def set_mode(self, channel, mode, master=None):
        if mode == self.CHANNEL_MODE_SLAVE:
            # master has to be given only if mode is 1
            if master in range(self.CHANNEL_MIN, self.CHANNEL_MAX + 1):
                if master is channel:
                    raise RuntimeError(
                        "Given master {} invalid. Must be different from the slave channel {}.".format(master, channel))
                else:
                    p2 = master
            else:
                raise RuntimeError("Given master {} invalid. Must be 1..8.".format(master))
        elif mode in (self.CHANNEL_MODE_INDEPENDENT, self.CHANNEL_MODE_EXTERN, self.CHANNEL_MODE_PCS,
                      self.CHANNEL_MODE_TEST):
            p2 = None
        else:
            raise RuntimeError("Given mode {} is unknown".format(mode))

        self._set_cmd(self.CMD_MODE, channel=channel, p1=mode, p2=p2)

    def get_mode(self, channel):
        response = self._get_cmd(self.CMD_MODE, channel)
        return int(response.get_value_1()), int(response.get_value_2())

    def zero_adjust(self, channel):
        # returns the voltage offset: -500 mV to 500 mV

        # actually this should be a "set" command, but it works easier with a "get" cmd
        response = self._get_cmd(self.CMD_ZERO_ADJUST, channel=channel, enable_query_token=False)
        return int(response.get_value_1())

    def set_high_limit(self, channel, high_limit):
        self._set_cmd(self.CMD_HIGH_LIMIT, channel=channel, setpoint_percentage=high_limit)

    def get_high_limit(self, channel):
        return self._from_raw_setpoint(self._get_cmd(self.CMD_HIGH_LIMIT, channel=channel).get_value_1())

    def set_low_limit(self, channel, low_limit):
        self._set_cmd(self.CMD_LOW_LIMIT, channel=channel, setpoint_percentage=low_limit)

    def get_low_limit(self, channel):
        return self._from_raw_setpoint(self._get_cmd(self.CMD_LOW_LIMIT, channel=channel).get_value_1())

    def set_trip_limits_mode(self, channel, mode):
        if mode not in self.TRIP_LIMIT_MODES:
            raise RuntimeError("Given mode {} invalid".format(mode))
        self._set_cmd(self.CMD_TRIPLE_LIMIT, channel=channel, p1=mode)

    def get_trip_limits_mode(self, channel):
        return int(self._get_cmd(self.CMD_TRIPLE_LIMIT, channel=channel).get_value_1())

    def set_gas_set(self, channel, gas_set, setpoint):
        if gas_set not in self.GAS_MENUS:
            raise RuntimeError("Given gas set {} invalid".format(gas_set))
        self._set_cmd(self.CMD_GAS_SET, channel=channel, p1=gas_set, setpoint_percentage=setpoint)

    #
    # def get_gas_set(self, channel, gas_set):
    #     # TODO: giving parameter when is_query=True?
    #     if gas_set not in self.GAS_MENUS:
    #         raise RuntimeError("Given gas set {} invalid".format(gas_set))
    #     return self._from_raw_setpoint(self._get_cmd(self.CMD_GAS_SET, channel=channel).get_value_1())

    def zero_adjust_pressure(self):
        # actually this should be a "set" command, but it works easier with a "get" cmd
        response = self._get_cmd(self.CMD_ZERO_ADJUST_PRESSURE, channel=channel, enable_query_token=False)
        return int(response.get_value_1())

    # def pressure_controller(self):
    #     cmd = "GT"
    #     controller_mode = 1 # 0..5
    #     return self.build_channel_grammar(cmd, channel=controller_mode)
    #
    # def pressure_controller_check(self):
    #     cmd = "GT"
    #     if query_write is "R"
    #     return self.build_channel_grammar(cmd, is_query=True)
    #
    # def pressure_unit_check(self):
    #     cmd = "PU"
    #     if query_write is "R"
    #     return self.build_channel_grammar(cmd, is_query=True)

    def open(self, channel):
        self._set_cmd(self.CMD_OPEN, channel=channel, channel_all_allowed=True)

    def close(self, channel):
        self._set_cmd(self.CMD_CLOSE, channel=channel, channel_all_allowed=True)


    # TODO: check these two methods. I dont really know what the controller
    # returns and how to interpret the result...
    def get_status_bit(self, channel, bit):
        status_decimal = int(self._get_cmd(self.CMD_STATUS, channel=channel, enable_query_token=False).get_value_1())
        if bit not in self.STATUS_BITS:
            raise RuntimeError("Given bit {} invalid".format(bit))
        return (status_decimal >> bit) & 1

    def get_status_all(self, channel):
        status_decimal = int(self._get_cmd(self.CMD_STATUS, channel=channel, enable_query_token=False).get_value_1())
        status = []
        for bit in self.STATUS_BITS:
            status.append((status_decimal >> bit) & 1)
        return status

    # def keyboard_disable(self):
    #     cmd = "KD"
    #     return self.build_channel_grammar(cmd)
    #
    # def keyboard_enable(self):
    #     cmd = "KE"
    #     return self.build_channel_grammar(cmd)
    #
    # def parameter_default(self): # set all parameters to default
    #     cmd = "DF"
    #     return self.build_channel_grammar(cmd)
    #
    # def hardware_reset(self): # performe a hardware reset, like power up
    #     cmd = "RE"
    #     return self.build_channel_grammar(cmd)
    #
    def identification(self): # check for identification
        return self._get_cmd(self.CMD_IDENTIFICATION, channel=channel, enable_query_token=False).get_value_1()

# MKS647CDriver.set_gas_range(MKS647CDriver.GAS_RANGE_5_SCCM)
# gas_range = MKS647CDriver.get_gas_range()
#
# if gas_range is MKS647CDriver.GAS_RANGE_5_SCCM:
#     pass
