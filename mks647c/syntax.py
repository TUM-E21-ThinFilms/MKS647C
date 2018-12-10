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

from typing import List
import re

DEBUG = True


class ArgumentNotSuppliedError(RuntimeError):
    pass


class ArgumentInvalidError(RuntimeError):
    pass


class Result(object):
    def __init__(self, match, data):
        self._match = False
        self._data = None

    def is_match(self):
        return self._match

    def set_match(self, match: bool):
        self._match = match

    def get_data(self):
        return self._data

    def set_data(self, data):
        self._data = data


class IntermediateResult:
    def __init__(self, data, length):
        self._data = data
        self._len = length

    def get_data(self):
        return self._data

    def get_length(self):
        return self._len


class Syntax(object):
    def __init__(self, name):
        self._name = name
        self._default = {}

    def get_name(self):
        return self._name

    def set_default(self, value):
        self._default[self._name] = value

    def get_parameter(self, name, *args, **kwargs):
        if kwargs is not None:
            if name in kwargs:
                return kwargs[name]

        if name in self._default:
            return self._default[name]
        raise ArgumentNotSuppliedError("No argument given for parameter: name = '" + name + "'")

    def parse(self, input):
        return NotImplementedError()

    def generate(self, *args, **kwargs):
        raise NotImplementedError()


class OptionalSyntax(Syntax):
    def __init__(self, name, sub_syntax):
        super(OptionalSyntax, self).__init__(name)
        self._syn = sub_syntax

    def parse(self, input):
        try:
            res = self._syn.parse(input)
            return IntermediateResult({**res.get_data(), **{self._name: True}}, res.get_length())
            # form: name, length
        except:
            return IntermediateResult({self._name: False}, 0)

    def generate(self, *args, **kwargs):

        opt = self.get_parameter(self._name, *args, **kwargs)

        if opt is True:
            return self._syn.generate(*args, **kwargs)
        else:
            return ""


class OrSyntax(Syntax):
    def __init__(self, name, syntaxes: List[Syntax]):
        super(OrSyntax, self).__init__(name)
        self._or = syntaxes

    def parse(self, input):
        for syn in self._or:
            result = syn.parse(input)
            if not result is None:
                return IntermediateResult({**result.get_data(), **{self._name: syn.get_name()}}, result.get_length())

    def generate(self, *args, **kwargs):
        data = self.get_parameter(self._name, *args, **kwargs)
        ret = ""
        for syn in self._or:
            if syn.get_name() in data:
                ret = ret + syn.generate(*args, **kwargs)
        return ret


class RepeatSyntax(Syntax):
    def __init__(self, name, syntax):
        super(RepeatSyntax, self).__init__(name)
        self._syn = syntax

    def parse(self, input):
        data = {self._name: (0, [])}
        i = 0
        length = 0
        while True:
            try:
                res = self._syn.parse(input)
                data[self._name].append(res.get_data())
                length = length + res.get_length()
                input = input[res.get_length():]
            except:
                break
            i = i + 1
        data[self._name][0] = i
        return IntermediateResult(data, length)

    def generate(self):
        raise NotImplementedError()


class ConcatSyntax(Syntax):
    def __init__(self, name, syntaxes: List[Syntax]):
        super(ConcatSyntax, self).__init__(name)
        self._syn = syntaxes

    def parse(self, input):
        length = 0
        data = {}

        for syn in self._syn:
            res = syn.parse(input)
            if res is None:
                return None
            data = {**data, **res.get_data()}
            length = length + res.get_length()
            input = input[res.get_length():]

        return IntermediateResult(data, length)

    def generate(self, *args, **kwargs):
        ret = ""
        for syn in self._syn:
            ret = ret + syn.generate(*args, **kwargs)
        return ret


class Token(Syntax):
    def __init__(self, name):
        super(Token, self).__init__(name)


class UntilStringToken(Token):
    def __init__(self, name, separator):
        super(UntilStringToken, self).__init__(name)
        if not isinstance(separator, str):
            raise RuntimeError("Separator must be a string")
        self._sep = separator

    def parse(self, input):
        try:
            pos = input.index(self._sep)
            return IntermediateResult({self._name: input[:pos]}, pos + len(self._sep))
        except ValueError:
            return None

    def generate(self, *args, **kwargs):
        return self.get_parameter(self._name, *args, **kwargs) + self._sep


class UntilToken(Token):
    def __init__(self, name, terminator):
        super(UntilToken, self).__init__(name)
        if not len(terminator) == 1:
            raise RuntimeError("terminator has to be of length 1")
        self._term = terminator

    def parse(self, input):
        for key, value in enumerate(input):
            if value == self._term:
                if key == 0:
                    return None
                return IntermediateResult({self._name: input[:key]}, key)

        return None

    def generate(self, *args, **kwargs):
        return self.get_parameter(self._name, *args, **kwargs) + self._term


class FixedLengthToken(Token):
    def __init__(self, name, length):
        super(FixedLengthToken, self).__init__(name)
        self._len = int(length)

    def parse(self, input):
        if len(input) >= self._len:
            return IntermediateResult({self._name: input[:self._len]}, self._len)

        return None

    def generate(self, *args, **kwargs):
        tk = self.get_parameter(self._name, *args, **kwargs)
        if not len(tk) == self._len:
            raise RuntimeError("parameter name = '" + self._name + "' must be of length 2")

        return tk


class RegexToken(Token):
    def __init__(self, name, regex, modifiers=0):
        super(RegexToken, self).__init__(name)
        self._regex = regex
        self._modifiers = modifiers

    def parse(self, input):
        m = re.search(self._regex, input, self._modifiers)

        if m is None:
            return None

        return IntermediateResult({self._name: m.groups()}, m.end())

    def _validate(self, tk):
        m = re.search(self._regex, tk)

        if m is None:
            raise RuntimeError("Given parameter with name = '" + self._name + "' does not match the regular expression")

    def generate(self, *args, **kwargs):
        tk = str(self.get_parameter(self._name, *args, **kwargs))
        self._validate(tk)
        return tk


class IntegerToken(RegexToken):
    def __init__(self, name):
        super(IntegerToken, self).__init__(name, r'\A([-]?\d+)')

    def parse(self, input):
        result = super(IntegerToken, self).parse(input)
        if result is None:
            return None

        return IntermediateResult({self._name: int(result.get_data()[self._name][0])}, result.get_length())


class FloatToken(RegexToken):
    def __init__(self, name):
        super(FloatToken, self).__init__(name, r'\A([-+]?(\d+([.,]\d*)?|[.,]\d+)([eE][-+]?\d+)?)')

    def parse(self, input):
        m = re.search(self._regex, input)

        if m is None:
            return None

        return IntermediateResult({self._name: float(m.group(1).replace(',', '.'))}, m.end())


class ConstantToken(RegexToken):
    def __init__(self, name, expect, case_sensitive=False, add_default=True):
        mod = re.IGNORECASE
        if case_sensitive is False:
            mod = 0

        super(ConstantToken, self).__init__(name, r"\A(" + re.escape(expect) + ")", mod)

        if add_default:
            self.set_default(expect)

        self._exp = expect

    def parse(self, input):
        result = super(ConstantToken, self).parse(input)

        if result is None:
            return None

        return IntermediateResult({self._name: result.get_data()[self._name][0]}, result.get_length())


class WhitespaceToken(RegexToken):
    def __init__(self, name):
        super(WhitespaceToken, self).__init__(name, r"\A(\s+)")

    def parse(self, input):
        result = super(WhitespaceToken, self).parse(input)

        if result is None:
            return None

        return IntermediateResult({self._name: result.get_data()[self._name][0]}, result.get_length())


class WordToken(RegexToken):
    def __init__(self, name):
        super(WordToken, self).__init__(name, r"\A(\w+)")

    def parse(self, input):
        result = super(WordToken, self).parse(input)

        if result is None:
            return None

        return IntermediateResult({self._name: result.get_data()[self._name][0]}, result.get_length())
