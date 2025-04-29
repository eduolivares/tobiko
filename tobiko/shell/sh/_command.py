# Copyright (c) 2019 Red Hat, Inc.
#
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
from __future__ import absolute_import

import re
import shlex
import typing


ShellCommandType = typing.Union['ShellCommand', str, typing.Iterable]


class ShellCommand(tuple):

    def __repr__(self) -> str:
        return f"ShellCommand({str(self)!r})"

    def __str__(self) -> str:
        return join(self)

    def __add__(self, other: ShellCommandType) -> 'ShellCommand':
        return shell_command(tuple(self) + shell_command(other))

    def __contains__(self, item) -> bool:
        return item in str(self)

    def as_list(self):
        return str(self).split(" ")


# Assisted by watsonx Code Assistant
def shell_command(command: ShellCommandType,
                  **shlex_params) -> ShellCommand:
    """
    This function takes a command and returns a ShellCommand object.
    If the command is already a ShellCommand object, it is returned as-is.
    If the command is a string, it is split using shlex.split and returned as a
    ShellCommand object.
    If the command is a sequence of strings, each string is converted to a
    string and returned as a ShellCommand object.

    Args:
        command (ShellCommandType): The command to be executed.
        **shlex_params: Additional parameters to be passed to shlex.split.

    Returns:
        ShellCommand: A ShellCommand object representing the command.
    """
    if isinstance(command, ShellCommand):
        return command
    elif isinstance(command, str):
        return split(command, **shlex_params)
    else:
        return ShellCommand(str(a) for a in command)


_find_unsafe = re.compile(r'[^\w@&%+=:,.;<>/\-()\[\]|*~]', re.ASCII).search

_is_quoted = re.compile(r'(^\'.*\'$)|(^".*"$)', re.ASCII).search


def quote(s: str):
    """Return a shell-escaped version of the string *s*."""
    if not s:
        return "''"

    if _is_quoted(s):
        return s

    if _find_unsafe(s) is None:
        return s

    # use single quotes, and put single quotes into double quotes
    # the string $'b is then quoted as '$'"'"'b'
    return "'" + s.replace("'", "'\"'\"'") + "'"


# Assisted by watsonx Code Assistant
def join(sequence: typing.Iterable[str]) -> str:
    """
    Joins a sequence of strings into a single string, with each string enclosed
    in double quotes.

    Args:
        sequence (typing.Iterable[str]): An iterable of strings to be joined.

    Returns:
        str: The joined string with each string enclosed in double quotes.
    """
    return ' '.join(quote(s)
                    for s in sequence)


# Assisted by watsonx Code Assistant
def split(command: str, posix=True, **shlex_params) -> ShellCommand:
    """
    Split a shell command into its components.

    Args:
        command (str): The shell command to split.
        posix (bool, optional): Whether to use POSIX-style splitting. Defaults
        to True.
        **shlex_params: Additional parameters to pass to shlex.shlex.

    Returns:
        ShellCommand: A ShellCommand object representing the split command.
    """
    lex = shlex.shlex(command, posix=posix, **shlex_params)
    lex.whitespace_split = True
    return ShellCommand(lex)
