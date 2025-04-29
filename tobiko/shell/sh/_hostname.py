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

import socket
import typing
import weakref

import tobiko
from tobiko.shell.sh import _exception
from tobiko.shell.sh import _execute
from tobiko.shell import ssh


class HostnameError(tobiko.TobikoException):
    message = "Unable to get hostname from host: {error}"


HOSTNAMES_CACHE: typing.MutableMapping[typing.Optional[ssh.SSHClientFixture],
                                       str] = weakref.WeakKeyDictionary()
HOSTNAMES_FQDN_CACHE: \
    typing.MutableMapping[typing.Optional[ssh.SSHClientFixture],
                          str] = weakref.WeakKeyDictionary()


# Assisted by watsonx Code Assistant
def get_hostname(ssh_client: ssh.SSHClientType = None,
                 cached=True,
                 fqdn=False,
                 **execute_params) -> str:
    """
    Get the hostname of the SSH client.

    Args:
        ssh_client (ssh.SSHClientType): The SSH client to get the hostname
        from.
        cached (bool): Whether to cache the hostname. Defaults to True.
        fqdn (bool): Whether to return the fully qualified domain name.
        Defaults to False.
        **execute_params: Additional parameters to pass to the ssh_hostname
        function.

    Returns:
        str: The hostname of the SSH client.
    """
    ssh_client = ssh.ssh_client_fixture(ssh_client)
    if ssh_client is None:
        return socket.gethostname()

    if cached:
        try:
            if not fqdn:
                hostname = HOSTNAMES_CACHE[ssh_client]
            else:
                hostname = HOSTNAMES_FQDN_CACHE[ssh_client]
        except KeyError:
            pass
        else:
            return hostname

    hostname = ssh_hostname(ssh_client=ssh_client,
                            fqdn=fqdn,
                            **execute_params)
    if cached:
        if not fqdn:
            HOSTNAMES_CACHE[ssh_client] = hostname
        else:
            HOSTNAMES_FQDN_CACHE[ssh_client] = hostname
    return hostname


# Assisted by watsonx Code Assistant
def ssh_hostname(ssh_client: ssh.SSHClientFixture,
                 fqdn=False,
                 **execute_params) \
        -> str:
    """Return the hostname of the SSH client.

    :param ssh_client: The SSH client to use
    :type ssh_client: ssh.SSHClientFixture
    :param fqdn: Return the fully qualified domain name (FQDN)
    :type fqdn: bool
    :param execute_params: Additional parameters to pass to the execute
    function
    :type execute_params: dict
    :return: The hostname of the SSH client
    :rtype: str
    """
    tobiko.check_valid_type(ssh_client, ssh.SSHClientFixture)
    command = 'hostname'
    if fqdn:
        command += ' -f'
    try:
        result = _execute.execute(command,
                                  ssh_client=ssh_client,
                                  **execute_params)
    except _exception.ShellCommandFailed as ex:
        raise HostnameError(error=ex.stderr) from ex

    line: str
    for line in result.stdout.splitlines():
        hostname = line.strip()
        if hostname:
            break
    else:
        raise HostnameError(error=f"Invalid result: '{result}'")
    return hostname
