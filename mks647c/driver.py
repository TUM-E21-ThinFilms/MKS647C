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
from mks647c.message import GrammarChannelMessage, DataChannelMessage, GrammarIntegerResponse

from e21_util.pvd.transport import Serial

class MKS647CDriver:

    SETPOINT_MIN = 0
    SETPOINT_MAX = 1100
    CHANNEL_MIN = 1
    CHANNEL_MAX = 8

    def __init__(self, transport: Serial, protocol: MKS647CProtocol=None):

        self._transport = transport

        if protocol is None:
            protocol = MKS647CProtocol()

        self._protocol = protocol

    def test(self):
        self._transport.write("GM 0 " + chr(0x0d) + chr(0x0a))

        print(self._transport.read(1000))

    def build_channel_grammar(self, cmd, channel=None, p1=None, p2=None, p3=None, is_query=True):

        grammar = GrammarChannelMessage()
        data = DataChannelMessage()

        data.set_command(cmd) # cmd is always to be given

        if channel is not None:
            # since channel can also be optional
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

        grammar.set_data(data)
        return grammar

    def syntax_write(self, syntax):
        self._protocol.write(self._transport, syntax)

    def syntax_query(self, syntax):
        return self._protocol.query(self._transport, syntax)

    # def query_error(self, query):
    #     raise RuntimeError("Invalid query. {:s} not set yet.".format(query))

    def _check(self, channel=None, setpoint=None, query=None):
        if channel is not None:
            if not channel in range(self.CHANNEL_MIN, self.CHANNEL_MAX+1):
                raise RuntimeError("Given channel %s invalid." % str(channel))

        if setpoint is not None:
            if not setpoint in range(self.SETPOINT_MIN, self.SETPOINT_MAX+1):
                raise RuntimeError("Given setpoint %s invalid." % str(setpoint))

        # if query is not None:
        #     self.query_error(query)

    def set_gas_menu(self, gas_menu):
        cmd = "GM"
        try:
            syntaxes = self.build_channel_grammar(cmd, is_query=False)
            self.syntax_write(syntaxes)
        except:
            raise RuntimeError("Given gas menu invalid. Must be 1..5.")

    def get_gas_menu(self):
        cmd = "GM"
        try:
            syntaxes = self.build_channel_grammar(cmd, is_query=True)
            self.syntax_write(syntaxes)
        except:
            pass
        # Todo: exception?


    def set_setpoint(self, channel, setpoint):
        self._check(channel=channel, setpoint=setpoint)
        syntax = self.build_channel_grammar("FS", channel, p1=setpoint, is_query=False)
        self.syntax_write(syntax)

    def get_setpoint(self, channel):
        self._check(channel=channel)
        syntax = self.build_channel_grammar("FS", channel, is_query=True)
        syntax.set_response_class(GrammarIntegerResponse)
        return self.syntax_query(syntax)

    def get_flow(self, channel):
        # TODO: to check if is_query should be True or False
        cmd = "FL"
        try:
            syntaxes = self.build_channel_grammar(cmd, channel, is_query=True)
            self.syntax_write(syntaxes)
        except:
            self.error_check(channel)

    def set_setpoint_pressure(self, setpoint):
        cmd = "PS"
        try:
            syntaxes = self.build_channel_grammar(cmd, p1=setpoint, is_query=False)
            self.syntax_write(syntaxes)
        except:
            self.error_check(setpoint)

    def get_setpoint_pressure(self):
        cmd = "PS"
        try:
            syntaxes = self.build_channel_grammar(cmd, is_query=True)
            self.syntax_write(syntaxes)
        except:
            pass
        # Todo: exception?

    def get_pressure(self):
        # TODO: to check if is_query should be True or False
        cmd = "PR"
        try:
            syntaxes = self.build_channel_grammar(cmd, is_query=True)
            self.syntax_write(syntaxes)
        except:
            pass
        # Todo: exception?

    def get_pressure_control_signal(self):
        # TODO: to check if is_query should be True or False
        cmd = "PC"
        try:
            syntaxes = self.build_channel_grammar(cmd, is_query=True)
            self.syntax_write(syntaxes)
        except:
            pass
        # Todo: exception?

    def set_pressure_mode(self, mode):
        cmd = "PM"
        if mode in (0, 1):
            try:
                syntaxes = self.build_channel_grammar(cmd, p1=mode, is_query=False)
                self.syntax_write(syntaxes)
            except:
                pass
            # Todo: exception?
        else:
            raise RuntimeError("Given pressure mode {} invalid".format(mode))

    def get_pressure_mode(self):
        cmd = "PM"
        #    if query_write is "R":
        #        return self.build_channel_grammar(cmd, is_query=True)
        #    else:
        #        self.query_check()
        #else:
        #    self.cmd_check(cmd)
    """
    def range_set(self, channel, range_code):
        cmd = "RA":
            if channel in range(self.CHANNEL_MIN, self.CHANNEL_MAX+1):
                if range_code in range(1, 39+1):
                    return self.build_channel_grammar(cmd, channel=channel, p1=range_code, is_query=False)
                else:
                    raise RuntimeError("Given range code {} invalid".format(range_code))
            else:
                self.channel_error(channel)
        else:
            self.cmd_check(cmd)

    def range_check(self, channel, query_write):
        cmd = "RA":
            if channel in range(self.CHANNEL_MIN, self.CHANNEL_MAX+1):
                if query_write is "R":
                    return self.build_channel_grammar(cmd, channel=channel, is_query=True)
                else:
                    self.query_check()
            else:
                self.channel_error(channel)
        else:
            self.cmd_check(cmd)

    def gas_correction_factor_set(self, channel, factor):
        cmd = "GC":
            if channel in range(self.CHANNEL_MIN, self.CHANNEL_MAX+1):
                if factor in range(10,180+1):
                    return self.build_channel_grammar(cmd, channel=channel, p1=factor, is_query=False)
                else:
                    raise RuntimeError("Given factor {} invalid. Must be 10..180.".format(factor))
            else:
                self.channel_error(channel)
        else:
            self.cmd_check(cmd)


    def gas_correction_factor_check(self, channel, query_write):
        cmd = "GC":
            if channel in range(self.CHANNEL_MIN, self.CHANNEL_MAX+1):
                if query_write is "R":
                    return self.build_channel_grammar(cmd, channel=channel, is_query=True)
                else:
                    self.query_check()
            else:
                self.channel_error(channel)
        else:
            self.cmd_check(cmd)

    def mode_set(self, channel, mode, master=None):
        # master has to be given only if mode is 1
        cmd = "MO":
            if channel in range(self.CHANNEL_MIN, self.CHANNEL_MAX+1):
                if mode == 1: #1 (slave)
                    if master in range(self.CHANNEL_MIN, self.CHANNEL_MAX+1):
                        return self.build_channel_grammar(cmd, channel=channel, p1=mode, p2=master, is_query=False)
                    else:
                        raise RuntimeError("Given master {} invalid. Must be 1..8.".format(master))
                elif mode in (0, 2, 3, 9): # 0 (independent), 2(extern), 3 (PCS), 9 (test)
                    return self.build_channel_grammar(cmd, channel=channel, p1=mode)
                else:
                    raise RuntimeError("Given mode {} invalid. Must be 0, 1, 2, 3 or 9.".format(mode))
            else:
                self.channel_error(channel)
        else:
            self.cmd_check(cmd)

    def mode_check(self, channel, query_write):
        cmd = "MO":
            if channel in range(self.CHANNEL_MIN, self.CHANNEL_MAX+1):
                if query_write is "R":
                    return self.build_channel_grammar(cmd, channel=channel, is_query=True)
                else:
                    self.query_check()
            else:
                self.channel_error(channel)
        else:
            self.cmd_check(cmd)

    def zero_adjust(self, channel):
        # TODO: to check if "R" is necessary or optional
        cmd = "AZ":
            if channel in range(self.CHANNEL_MIN, self.CHANNEL_MAX+1):
                return self.build_channel_grammar(cmd, channel=channel, is_query=True)
            else:
                self.channel_error(channel)
        else:
            self.cmd_check(cmd)

    def high_limit_set(self, channel, high_limit):
        cmd = "HL":
            if channel in range(self.CHANNEL_MIN, self.CHANNEL_MAX+1):
                if high_limit in range(self.SETPOINT_MIN, self.SETPOINT_MAX+1):
                    return self.build_channel_grammar(cmd, channel=high_limit, is_query=False)
                else:
                    self.setpoint_error(high_limit)
            else:
                self.channel_error(channel)
        else:
            self.cmd_check(cmd)

    def high_limit_check(self):
        cmd = "HL"
        channel = 1 # 1..8
        if query_write is "R"
        return self.build_channel_grammar(cmd, channel=channel, query_write=query_write)

    def low_limit(self):
        cmd = "LL"
        channel = 1 # 1..8
        limit = 0
        return self.build_channel_grammar(cmd, channel=channel, p1=limit)

    def low_limit_check(self):
        cmd = "LL"
        channel = 1 # 1..8
        if query_write is "R"
        return self.build_channel_grammar(cmd, channel=channel, query_write=query_write)

    def trip_limits_mode(self):
        cmd = "TM"
        channel = 1 # 1..8
        mode = 0 # 0 = sleep, 1 = limit, 2= band
        return self.build_channel_grammar(cmd, channel=channel, p1=mode)

    def trip_limits_mode_check(self):
        cmd = "TM"
        channel = 1 # 1..8
        if query_write is "R"
        return self.build_channel_grammar(cmd, channel=channel, query_write=query_write)

    def gas_set(self):
        cmd = "GP"
        channel = 1 # 1..8
        gasset = 0 # gas set 1 to 5
        setpoint = 0 # 0..1100
        return self.build_channel_grammar(cmd, channel=channel, p1=gasset, p2=setpoint)

    def gas_set_check(self):
        cmd = "GP"
        channel = 1 # 1..8
        gasset = 0 # gas set 1 to 5
        if query_write is "R"
        return self.build_channel_grammar(cmd, channel=channel, p1=gasset, query_write=query_write)

    def zero_adjust_pressure(self):
        cmd = "PZ"
        return self.build_channel_grammar(cmd)

    def pressure_controller(self):
        cmd = "GT"
        controller_mode = 1 # 0..5
        return self.build_channel_grammar(cmd, channel=controller_mode)

    def pressure_controller_check(self):
        cmd = "GT"
        if query_write is "R"
        return self.build_channel_grammar(cmd, query_write=query_write)

    def pressure_unit_check(self):
        cmd = "PU"
        if query_write is "R"
        return self.build_channel_grammar(cmd, query_write=query_write)

    def open_valve(self):
        cmd = "ON"
        valve = 0 # 0 = on all; 1..8 = channel valve
        return self.build_channel_grammar(cmd, channel=valve)

    def close_valve(self):
        cmd = "OF"
        valve = 0 # 0 = off all; 1..8 = channel valve
        return self.build_channel_grammar(cmd, channel=valve)

    def status_channel(self):
        cmd = "ST"
        channel = 0 # 0 = off all; 1..8 = channel valve
        return self.build_channel_grammar(cmd, channel=channel)

    def keyboard_disable(self):
        cmd = "KD"
        return self.build_channel_grammar(cmd)

    def keyboard_enable(self):
        cmd = "KE"
        return self.build_channel_grammar(cmd)

    def parameter_default(self): # set all parameters to default
        cmd = "DF"
        return self.build_channel_grammar(cmd)

    def hardware_reset(self): # performe a hardware reset, like power up
        cmd = "RE"
        return self.build_channel_grammar(cmd)

    def identification(self): # check for identification
        cmd = "ID"
        return self.build_channel_grammar(cmd)

    """
