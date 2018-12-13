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
    # FL c: check for actual flow of a channel
    # PR: check for pressure
    # PC: check for PCS (pressure control signal)
    # AZ c: zero adjust MFC, aber man bekommt ein Offset-Wert zurück
    # PZ: zero adjust pressure, aber man bekommt ein Offset-Wert zurück
    # ST c: check for status of a channel
    # ID: check for identification
    #
    # CMD(s) mit R und Parameters geleichzeitig:
    # GP c s R: check for setpoint in gas set, wofür man auch s=gas_set eingeben muss
    #
    # CMD(s) wo die Channels auch null sein darf:
    # ON c: open valve, wo c=0 entspricht ON ALL
    # OF c: close valve, wo c=0 entspricht OFF ALL
    #
    #


    CMD_GAS_MENU = 'GM'
    CMD_SETPOINT = 'FS'
    CMD_FLOW = 'FL'
    CMD_PRESSURE = 'PS'
    CMD_PRESSURE_MODE = 'PM'
    CMD_RANGE = 'RA'
    CMD_GAS_CORRECTION_FACTOR = 'GC'
    CMD_MODE = 'MO'
    CMD_HIGH_LIMIT = 'HL'
    CMD_LOW_LIMIT = 'LL'
    CMD_TRIPLE_LIMIT = 'TM'
    CMD_GAS_SET = 'GP'



    SETPOINT_MIN = 0
    SETPOINT_MAX = 1100

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

    CHANNEL_MODE_INDEPENDENT = 0
    CHANNEL_MODE_SLAVE = 1
    CHANNEL_MODE_EXTERN = 2
    CHANNEL_MODE_PCS = 3
    CHANNEL_MODE_TEST = 9


    def __init__(self, transport: Serial, protocol: MKS647CProtocol = None):

        self._transport = transport

        if protocol is None:
            protocol = MKS647CProtocol()

        self._protocol = protocol

    def _build_msg(self, cmd, channel=None, p1=None, p2=None, p3=None, is_query=True):
        # works also for cmds that do not need any channel
        # 'R' for request, however, is incompatible with parameters p1..p3
        # TODO: adjust it for the cmd 'GP' or write a new method for it (also the syntax class etc)

        msg = GrammarChannelMessage()
        data = DataChannelMessage()

        data.set_command(cmd)  # cmd is always to be given

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

    def _check(self, channel=None, raw_setpoint=None):
        if channel is not None:
            if channel not in range(self.CHANNEL_MIN, self.CHANNEL_MAX + 1):
                raise RuntimeError("Given channel %s invalid." % str(channel))

        if raw_setpoint is not None:
            if raw_setpoint not in range(self.SETPOINT_MIN, self.SETPOINT_MAX + 1):
                raise RuntimeError("Given setpoint %s invalid." % str(raw_setpoint))

    def _get_cmd(self, cmd, channel=None):
        # works only for cmds with R but without extra parameters p1..p3
        # If a setpoint is got, it will be returned in an integer form to the explicit method, which must convert it
        # into a natural form by itself
        self._check(channel=channel)
        msg = self._build_msg(cmd, channel=channel, is_query=True)
        msg.set_response_class(GrammarIntegerResponse)
        response = self._query_message(msg)
        self._check_data_existing(response)
        return response

    def _set_cmd(self, cmd, channel=None, p1=None, p2=None, setpoint_percentage=None):
        # practically no p3 will be transferred according to the manual
        if setpoint_percentage is not None:
            raw_setpoint = self._to_raw_setpoint(setpoint_percentage)
            self._check(raw_setpoint=raw_setpoint)
            if p1 is not None:
                p2 = raw_setpoint
            else:
                p1 = raw_setpoint
        self._check(channel=channel)
        msg = self._build_msg(cmd, channel=channel, p1=p1, p2=p2, is_query=False)
        return self._write_message(msg)

    @staticmethod
    def _to_raw_setpoint(setpoint_percentage):
        return round(float(setpoint_percentage) * 1000.0) # from float (0, 1.1) to integer (0, 1100)

    @staticmethod
    def _from_raw_setpoint(setpoint_raw):
        return float(setpoint_raw) / 1000.0 # from integer (0, 1100) to float (0, 1.1)

    @staticmethod
    def _to_raw_correction_factor(correction_factor_percentage):
        return round(float(correction_factor_percentage) * 100.0) # from float (0.1, 1.8) to integer (10, 180)

    @staticmethod
    def _from_raw_correction_factor(correction_factor_raw):
        return float(correction_factor_raw) / 100.0 # from integer (10, 180) to float (0.1, 1.8)

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
        return self._from_raw_setpoint(self._get_cmd(self.CMD_FLOW, channel).get_value_1())

    def set_pressure(self, setpoint_percentage):
        self._set_cmd(self.CMD_PRESSURE, setpoint_percentage=setpoint_percentage)

    def get_pressure_setpoint(self):
        return self._from_raw_setpoint(self._get_cmd(self.CMD_PRESSURE).get_value_1())

    # def get_pressure(self):
    #     # TODO: to check if it's okay to have "R" in the input
    #     syntax = self._build_msg("PR", is_query=True)
    #     syntax.set_response_class(GrammarIntegerResponse)
    #     return self._query_message(syntax)
    #
    # def get_pressure_control_signal(self):
    #     # TODO: to check if it's okay to have "R" in the input
    #     syntax = self._build_msg("PC", is_query=True)
    #     syntax.set_response_class(GrammarIntegerResponse)
    #     return self._query_message(syntax)

    def set_pressure_mode(self, mode):
        if mode not in self.PRESSURE_MODES:
            raise RuntimeError("Given pressure mode {} invalid".format(mode))
        self._set_cmd(self.CMD_PRESSURE_MODE, p1=mode)

    def get_pressure_mode(self):
        return int(self._get_cmd(self.CMD_PRESSURE_MODE).get_value_1())

    def set_range(self, channel, range_code):
        if range_code not in range(0, 39 + 1):
            raise RuntimeError("Given range code invalid.")
        self._set_cmd(self.CMD_RANGE, channel=channel, p1=range_code)

    def get_range(self, channel):
        return int(self._get_cmd(self.CMD_RANGE, channel=channel).get_value_1())

    def set_gas_correction_factor(self, channel, factor_percentage):
        if 0.1 < factor_percentage < 1.8:
            raw_factor = self._to_raw_correction_factor(factor_percentage)
        else:
            raise RuntimeError("Given gas correction factor {} invalid.".format(factor_percentage))
        self._set_cmd(self.CMD_GAS_CORRECTION_FACTOR, channel=channel, p1=raw_factor)

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
                      self.CHANNEL_MODE_TEST):  # 0 (independent), 2(extern), 3 (PCS), 9 (test)
            p2 = None
        else:
            raise RuntimeError("Given mode {} invalid. Must be 0, 1, 2, 3 or 9.".format(mode))
        self._set_cmd(self.CMD_MODE, channel=channel, p1=mode, p2=p2)

    def get_mode(self, channel):
        # TODO: die 2. Wert optional?
        return int(self._get_cmd(self.CMD_MODE, channel).get_value_1())

    # def zero_adjust(self, channel):
    #     # TODO: to check if "R" is necessary or optional
    #     cmd = "AZ":
    #         if channel in range(self.CHANNEL_MIN, self.CHANNEL_MAX+1):
    #             return self.build_channel_grammar(cmd, channel=channel, is_query=True)
    #         else:
    #             self.channel_error(channel)
    #     else:
    #         self.cmd_check(cmd)

    def set_high_limit(self, channel, high_limit):
        self._check(channel=channel, raw_setpoint=high_limit)
        syntax = self._build_msg(self.CMD_HIGH_LIMIT, channel=channel, p1=high_limit, is_query=False)
        self._write_message(syntax)

    def get_high_limit(self, channel):
        self._check(channel=channel)
        syntax = self._build_msg(self.CMD_HIGH_LIMIT, channel=channel, is_query=True)
        syntax.set_response_class(GrammarIntegerResponse)
        return self._query_message(syntax)

    def set_low_limit(self, channel, low_limit):
        self._check(channel=channel, raw_setpoint=low_limit)
        syntax = self._build_msg(self.CMD_LOW_LIMIT, channel=channel, p1=low_limit, is_query=False)
        self._write_message(syntax)

    def get_low_limit(self, channel):
        self._check(channel=channel)
        syntax = self._build_msg(self.CMD_LOW_LIMIT, channel=channel, is_query=True)
        syntax.set_response_class(GrammarIntegerResponse)
        return self._query_message(syntax)

    def set_trip_limits_mode(self, channel, mode):
        # TODO: explicitly define the meanings of modes
        self._check(channel=channel)
        if mode in (0, 1, 2):  # 0 = sleep, 1 = limit, 2= band
            syntax = self._build_msg(self.CMD_TRIPLE_LIMIT, channel=channel, p1=mode, is_query=False)
            self._write_message(syntax)
        else:
            raise RuntimeError("Given mode {} invalid. Must be 0, 1 or 2.".format(mode))

    def get_trip_limits_mode(self, channel):
        self._check(channel=channel)
        syntax = self._build_msg(self.CMD_TRIPLE_LIMIT, channel=channel, is_query=True)
        syntax.set_response_class(GrammarIntegerResponse)
        return self._query_message(syntax)

    def gas_set(self, channel, gas_set, setpoint):
        # TODO: explicitly define the meanings of gas sets
        self._check(channel=channel, raw_setpoint=setpoint)
        if gas_set in range(1, 6):
            syntax = self._build_msg(self.CMD_GAS_SET, channel=channel, p1=gas_set, p2=setpoint, is_query=False)
            self._write_message(syntax)
        else:
            raise RuntimeError("Given gas set {} invalid. Must be 1..5.".format(gas_set))

    def get_setpoint_gas_set(self, channel, gas_set):
        # TODO: giving parameter when is_query=True?
        # TODO: explicitly define the meanings of gas sets
        self._check(channel=channel)
        if gas_set in range(1, 6):
            syntax = self._build_msg(self.CMD_GAS_SET, channel=channel, p1=gas_set, is_query=True)
            syntax.set_response_class(GrammarIntegerResponse)
            return self._query_message(syntax)

    # def zero_adjust_pressure(self):
    #     cmd = "PZ"
    #     return self.build_channel_grammar(cmd)
    #
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
    #
    # def open_valve(self):
    #     cmd = "ON"
    #     valve = 0 # 0 = on all; 1..8 = channel valve
    #     return self.build_channel_grammar(cmd, channel=valve)
    #
    # def close_valve(self):
    #     cmd = "OF"
    #     valve = 0 # 0 = off all; 1..8 = channel valve
    #     return self.build_channel_grammar(cmd, channel=valve)

    def get_channel_status(self, channel):
        self._check(channel=channel)
        syntax = self._build_msg("ST", channel=channel, is_query=True)
        syntax.set_response_class(GrammarIntegerResponse)
        return self._query_message(syntax)

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
    # def identification(self): # check for identification
    #     cmd = "ID"
    #     return self.build_channel_grammar(cmd)


# MKS647CDriver.set_gas_range(MKS647CDriver.GAS_RANGE_5_SCCM)
# gas_range = MKS647CDriver.get_gas_range()
#
# if gas_range is MKS647CDriver.GAS_RANGE_5_SCCM:
#     pass