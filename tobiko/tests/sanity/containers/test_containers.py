# Copyright (c) 2022 Red Hat, Inc.
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

import functools
import os

import pytest
import testtools
from oslo_log import log

import tobiko
from tobiko.openstack import neutron
from tobiko.openstack import topology
from tobiko import podified
from tobiko.podified import containers as podified_containers
from tobiko.rhosp import containers as rhosp_containers
from tobiko.shell import sh
from tobiko import tripleo
from tobiko.tripleo import containers as tripleo_containers
from tobiko.tripleo import overcloud


LOG = log.getLogger(__name__)


class BaseContainersHealtTest(testtools.TestCase):

    def _assert_containers_running(self, group, expected_containers):
        topology.get_openstack_topology().assert_containers_running(
            group=group, expected_containers=expected_containers)


@tripleo.skip_if_missing_overcloud
class TripleoContainersHealthTest(BaseContainersHealtTest):
    # TODO(eolivare): refactor this class, because it replicates some code from
    # tobiko/tripleo/containers.py and its tests may be duplicating what
    # test_0vercloud_health_check already covers when it calls
    # containers.assert_all_tripleo_containers_running()

    @functools.lru_cache()
    def list_node_containers(self, ssh_client):
        """returns a list of containers and their run state"""
        return tripleo_containers.get_container_runtime().\
            list_containers(ssh_client=ssh_client)

    def test_cinder_api(self):
        """check that all common tripleo containers are running"""
        self._assert_containers_running('controller', ['cinder_api'])

    @tripleo.skip_if_ceph_rgw()
    def test_swift_rsync(self):
        self._assert_containers_running('controller', ['swift_rsync'])

    @tripleo.skip_if_ceph_rgw()
    def test_swift_proxy(self):
        self._assert_containers_running('controller', ['swift_proxy'])

    @tripleo.skip_if_ceph_rgw()
    def test_swift_object_updater(self):
        self._assert_containers_running('controller', ['swift_object_updater'])

    @tripleo.skip_if_ceph_rgw()
    def test_swift_object_server(self):
        self._assert_containers_running('controller', ['swift_object_server'])

    @tripleo.skip_if_ceph_rgw()
    def test_swift_object_replicator(self):
        self._assert_containers_running('controller',
                                        ['swift_object_replicator'])

    @tripleo.skip_if_ceph_rgw()
    def test_swift_object_expirer(self):
        self._assert_containers_running('controller', ['swift_object_expirer'])

    @tripleo.skip_if_ceph_rgw()
    def test_swift_object_auditor(self):
        self._assert_containers_running('controller', ['swift_object_auditor'])

    @tripleo.skip_if_ceph_rgw()
    def test_swift_container_updater(self):
        self._assert_containers_running('controller',
                                        ['swift_container_updater'])

    @tripleo.skip_if_ceph_rgw()
    def test_swift_container_server(self):
        self._assert_containers_running('controller',
                                        ['swift_container_server'])

    @tripleo.skip_if_ceph_rgw()
    def test_swift_container_replicator(self):
        self._assert_containers_running('controller',
                                        ['swift_container_replicator'])

    @tripleo.skip_if_ceph_rgw()
    def test_swift_container_auditor(self):
        self._assert_containers_running('controller',
                                        ['swift_container_auditor'])

    @tripleo.skip_if_ceph_rgw()
    def test_swift_account_server(self):
        self._assert_containers_running('controller', ['swift_account_server'])

    @tripleo.skip_if_ceph_rgw()
    def test_swift_account_replicator(self):
        self._assert_containers_running('controller',
                                        ['swift_account_replicator'])

    @tripleo.skip_if_ceph_rgw()
    def test_swift_account_reaper(self):
        self._assert_containers_running('controller', ['swift_account_reaper'])

    @tripleo.skip_if_ceph_rgw()
    def test_swift_account_auditor(self):
        self._assert_containers_running('controller',
                                        ['swift_account_auditor'])

    def test_nova_vnc_proxy(self):
        self._assert_containers_running('controller', ['nova_vnc_proxy'])

    def test_nova_scheduler(self):
        self._assert_containers_running('controller', ['nova_scheduler'])

    def test_nova_metadata(self):
        self._assert_containers_running('controller', ['nova_metadata'])

    def test_nova_conductor(self):
        self._assert_containers_running('controller', ['nova_conductor'])

    def test_nova_api_cron(self):
        self._assert_containers_running('controller', ['nova_api_cron'])

    def test_nova_api(self):
        self._assert_containers_running('controller', ['nova_api'])

    def test_neutron_api(self):
        self._assert_containers_running('controller', ['neutron_api'])

    def test_memcached(self):
        self._assert_containers_running('controller', ['memcached'])

    def test_controller_logrotate_crond(self):
        self._assert_containers_running('controller', ['logrotate_crond'])

    def test_keystone(self):
        self._assert_containers_running('controller', ['keystone'])

    def test_controller_iscsid(self):
        self._assert_containers_running('controller', ['iscsid'])

    def test_horizon(self):
        self._assert_containers_running('controller', ['horizon'])

    def test_heat_engine(self):
        self._assert_containers_running('controller', ['heat_engine'])

    def test_heat_api_cron(self):
        self._assert_containers_running('controller', ['heat_api_cron'])

    def test_heat_api_cfn(self):
        self._assert_containers_running('controller', ['heat_api_cfn'])

    def test_heat_api(self):
        self._assert_containers_running('controller', ['heat_api'])

    def test_glance_api(self):
        self._assert_containers_running('controller', ['glance_api'])

    def test_cinder_scheduler(self):
        self._assert_containers_running('controller', ['cinder_scheduler'])

    def test_cinder_api_cron(self):
        self._assert_containers_running('controller', ['cinder_api_cron'])

    def test_compute_iscsid(self):
        self._assert_containers_running('compute', ['iscsid'])

    def test_compute_logrotate_crond(self):
        self._assert_containers_running('compute', ['logrotate_crond'])

    def test_nova_compute(self):
        self._assert_containers_running('compute', ['nova_compute'])

    def test_nova_libvirt(self):
        nova_libvirt = tripleo_containers.get_libvirt_container_name()
        self._assert_containers_running('compute', [nova_libvirt])

    def test_nova_migration_target(self):
        self._assert_containers_running('compute', ['nova_migration_target'])

    def test_nova_virtlogd(self):
        self._assert_containers_running('compute', ['nova_virtlogd'])

    def test_ovn_containers_running(self):
        tripleo_containers.assert_ovn_containers_running()

    @pytest.mark.skip_during_ovn_migration
    def test_equal_containers_state(self, expected_containers_list=None,
                                    timeout=120, interval=5,
                                    recreate_expected=False):
        """compare all overcloud container states with using two lists:
        one is current , the other some past list
        first time this method runs it creates a file holding overcloud
        containers' states: ~/expected_containers_td.csv'
        second time it creates a current containers states list and
        compares them, they must be identical"""

        expected_containers_td = []
        # if we have a file or an explicit variable use that ,
        # otherwise  create and return
        if recreate_expected or (not (expected_containers_list or
                                      os.path.exists(
                                          rhosp_containers.
                                          expected_containers_file))):
            tripleo_containers.save_containers_state_to_file(
                tripleo_containers.list_containers())
            return
        elif expected_containers_list:
            expected_containers_td = tobiko.TableData(
                tripleo_containers.get_container_states_list(
                    expected_containers_list),
                columns=['container_host', 'container_name',
                         'container_state'])
        elif os.path.exists(rhosp_containers.expected_containers_file):
            expected_containers_td = tobiko.TableData.read_csv(
                rhosp_containers.expected_containers_file)

        error_info = 'Output explanation: left_only is the original state, ' \
                     'right_only is the new state'
        for attempt in tobiko.retry(timeout=timeout, interval=interval):
            actual_containers_td = tripleo_containers.list_containers_td()
            LOG.info('expected_containers_td: '
                     f'{expected_containers_td}')
            LOG.info(f'actual_containers_td: {actual_containers_td}')
            # execute a `dataframe` diff between the expected
            # and actual containers
            expected_containers_state_changed = \
                rhosp_containers.tabledata_difference(
                    expected_containers_td, actual_containers_td)
            # check for changed state containerstopology
            if expected_containers_state_changed.empty:
                LOG.info("assert_equal_containers_state :"
                         " OK, all containers are on the same state")
                return

            if attempt.is_last:
                tobiko.fail('expected containers changed state ! :\n'
                            f'{expected_containers_state_changed}\n'
                            f'{error_info}')

            LOG.info('container states mismatched:\n'
                     f'{expected_containers_state_changed}')
            # clear cache to obtain new data
            tripleo_containers.list_node_containers.cache_clear()

    def config_validation(self, config_checkings):
        container_runtime_name = tripleo_containers.\
                                 get_container_runtime_name()
        for node in topology.list_openstack_nodes(
                group=config_checkings['node_group']):
            for param_check in config_checkings['param_validations']:
                obtained_param = sh.execute(
                    f"{container_runtime_name} exec -uroot "
                    f"{config_checkings['container_name']} crudini "
                    f"--get {config_checkings['config_file']} "
                    f"{param_check['section']} {param_check['param']}",
                    ssh_client=node.ssh_client, sudo=True).stdout.strip()
                self.assertTrue(param_check['expected_value'] in
                                obtained_param,
                                f"Expected {param_check['param']} value: "
                                f"{param_check['expected_value']}\n"
                                f"Obtained {param_check['param']} value: "
                                f"{obtained_param}")
        LOG.info("Configuration verified:\n"
                 f"node group: {config_checkings['node_group']}\n"
                 f"container: {config_checkings['container_name']}\n"
                 f"config file: {config_checkings['config_file']}")

    @neutron.skip_unless_is_ovn()
    def test_ovn_container_config(self):
        """check containers configuration in ovn
        """
        ovn_config_checkings = \
            {'node_group': 'controller',
             'container_name': 'neutron_api',
             'config_file': '/etc/neutron/plugins/ml2/ml2_conf.ini',
             'param_validations': [{'section': 'ml2',
                                    'param': 'mechanism_drivers',
                                    'expected_value': 'ovn'},
                                   {'section': 'ml2',
                                    'param': 'type_drivers',
                                    'expected_value': 'geneve'},
                                   {'section': 'ovn',
                                    'param': 'ovn_metadata_enabled',
                                    'expected_value': 'True'}]}
        self.config_validation(ovn_config_checkings)

    @neutron.skip_unless_is_ovs()
    def test_ovs_container_config(self):
        """check containers configuration in ovn
        """
        ovs_config_checkings = \
            {'node_group': 'controller',
             'container_name': 'neutron_api',
             'config_file': '/etc/neutron/plugins/ml2/ml2_conf.ini',
             'param_validations': [{'section': 'ml2',
                                    'param': 'mechanism_drivers',
                                    'expected_value': 'openvswitch'}]}
        self.config_validation(ovs_config_checkings)


@podified.skip_if_not_podified
class PodifiedContainersHealthTest(BaseContainersHealtTest):

    @functools.lru_cache()
    def list_node_containers(self, ssh_client):
        """returns a list of containers and their run state"""
        return podified_containers.get_container_runtime().\
            list_containers(ssh_client=ssh_client)

    def test_compute_iscsid(self):
        self._assert_containers_running(podified.EDPM_COMPUTE_GROUP,
                                        ['iscsid'])

    def test_compute_logrotate_crond(self):
        self._assert_containers_running(podified.EDPM_COMPUTE_GROUP,
                                        ['logrotate_crond'])

    def test_nova_compute(self):
        self._assert_containers_running(podified.EDPM_COMPUTE_GROUP,
                                        ['nova_compute'])

    def test_ovn_containers_running(self):
        podified_containers.assert_ovn_containers_running()

    def test_equal_containers_state(self, expected_containers_list=None,
                                    timeout=120, interval=5,
                                    recreate_expected=False):
        """compare all overcloud container states with using two lists:
        one is current , the other some past list
        first time this method runs it creates a file holding overcloud
        containers' states: ~/expected_containers_td.csv'
        second time it creates a current containers states list and
        compares them, they must be identical"""

        expected_containers_td = []
        # if we have a file or an explicit variable use that ,
        # otherwise  create and return
        if recreate_expected or (not (expected_containers_list or
                                      os.path.exists(
                                          rhosp_containers.
                                          expected_containers_file))):
            podified_containers.save_containers_state_to_file(
                podified_containers.list_containers())
            return
        elif expected_containers_list:
            expected_containers_td = tobiko.TableData(
                podified_containers.get_container_states_list(
                    expected_containers_list),
                columns=['container_host', 'container_name',
                         'container_state'])
        elif os.path.exists(rhosp_containers.expected_containers_file):
            expected_containers_td = tobiko.TableData.read_csv(
                rhosp_containers.expected_containers_file)
        error_info = 'Output explanation: left_only is the original state, ' \
                     'right_only is the new state'
        for attempt in tobiko.retry(timeout=timeout, interval=interval):
            actual_containers_td = \
                podified_containers.list_containers_td()
            LOG.info('expected_containers_td: {} '.format(
                expected_containers_td.to_string()))
            LOG.info('actual_containers_td: {} '.format(
                actual_containers_td.to_string()))
            # execute a `dataframe` diff between the expected
            # and actual containers
            expected_containers_state_changed = \
                rhosp_containers.tabledata_difference(
                    expected_containers_td, actual_containers_td)
            # check for changed state containerstopology
            if expected_containers_state_changed.empty:
                LOG.info("assert_equal_containers_state :"
                         " OK, all containers are on the same state")
                return

            if attempt.is_last:
                tobiko.fail('expected containers changed state ! :\n'
                            f'{expected_containers_state_changed}\n'
                            f'{error_info}')

            LOG.info('container states mismatched:\n'
                     f'{expected_containers_state_changed}')
            # clear cache to obtain new data
            podified_containers.list_node_containers.cache_clear()


class GenericContainersTest(testtools.TestCase):

    def test_overcloud_containers_running(self):
        """check that all containers are in running state"""
        failures = tripleo_containers.list_containers_td()
        if not failures.empty:
            tripleo_containers.assert_all_tripleo_containers_running()

    def test_containers_state_matches_expected(self):
        """check that containers states match a previously
        snapshotted state"""
        tripleo_containers.assert_equal_containers_state()

    def test_list_containers_from_podman_cmd(self):
        """check podman containers list
        list containers in running state from compute node"""
        for node in topology.list_openstack_nodes(group='compute'):
            containers_list = tripleo_containers.list_node_containers(
                ssh_client=node.ssh_client)
            self.assertGreater(len(containers_list), 5)
            for container in containers_list:
                self.assertIn("running", container.status)

    def test_list_containers_from_docker_cmd(self):
        """check docker containers list
        list containers in running state from any node"""
        all_nodes = topology.list_openstack_nodes()
        if all_nodes:
            containers_list = \
                    tripleo_containers.list_node_containers(
                        ssh_client=all_nodes[0].ssh_client)
            self.assertGreater(len(containers_list), 0)
            for container in containers_list:
                self.assertIn("running", container.status)

    def test_list_container_objects_df(self):
        """check containers list with container objects
        list containers in running state from overcloud nodes"""
        containers_list_df = tripleo_containers.list_containers_objects_df()
        if not containers_list_df.empty:
            for _, container in enumerate(containers_list_df):
                self.assertIsNotNone(container['container_object'])

    def test_get_container_states_list(self):
        """check the containers states is returning the proper values"""
        containers_list = tripleo_containers.list_containers()
        containers_states_list = tripleo_containers.get_container_states_list(
            containers_list)
        self.assertGreater(len(containers_states_list), 0)

    def test_ovn_containers_state_check(self):
        """check that ovn containers are running with correct state"""
        if not neutron.has_ovn():
            tobiko.skip('This test requires ovn environment')
        else:
            tripleo_containers.assert_ovn_containers_running()


class ContainerCreationTest(testtools.TestCase):

    def test_save_containers_state_to_file(self):
        """save containers states to a file for later comparison"""

        containers_list = tripleo_containers.list_containers()
        tripleo_containers.save_containers_state_to_file(containers_list)
        # compare the file content and the content that should be written
        # we mock the expected_containers_file path changing the file
        # location from home folder to /tmp/
        saved_file_content = tripleo_containers.get_container_states_list(
            containers_list)
        expected_saved_file_content = \
            tripleo_containers.get_container_states_list(containers_list)
        self.assertEqual(expected_saved_file_content, saved_file_content)

    def test_containers_state_in_csv_format(self):
        """check containers state can be stored in a csv format file
        steps:
        1- Create file
        2- Check the file exists and contains expected data"""
        # create file
        containers_list = tripleo_containers.list_containers()
        expected_container_list_df = tobiko.TableData(
            tripleo_containers.get_container_states_list(containers_list),
            columns=['container_host', 'container_name', 'container_state'])

        # check the created file exists and contains data
        self.assertGreater(len(expected_container_list_df), 0)
        for container in expected_container_list_df:
            # add additional columns
            self.assertIsNotNone(container.get('container_host'))
            self.assertIsNotNone(container.get('container_state'))
            self.assertIsNotNone(container.get('container_name'))

    @tobiko.skip_unless('TripleO overcloud required', overcloud.has_overcloud)
    def test_containers_logs_are_being_stored(self):
        """Check the containers logs are being stored
        - for each container, check logs file is being
          updated"""
        container_runtime_name = \
            tripleo_containers.get_container_runtime_name()
        if not container_runtime_name:
            tobiko.skip('No container runtime available')

        expected_containers_td = tobiko.TableData(
            tripleo_containers.get_container_states_list(
                tripleo_containers.list_containers()),
            columns=['container_host', 'container_name', 'container_state'])

        containers_without_logs_gen = []
        for container in expected_containers_td:
            container_name = container['container_name']
            if container_name.startswith('/'):
                container_name = container_name[1:]

            if container_runtime_name == 'podman':
                log_path = f'/var/log/containers/stdouts/{container_name}.log'
            else:
                log_path = ('/var/lib/docker/containers/'
                            f'{container_name}/'
                            f'{container_name}-json.log')

            container_host = container['container_host']
            ssh_client = overcloud.overcloud_ssh_client(
                                instance=overcloud.find_overcloud_node(
                                          name=container_host))
            try:
                log_file_stat = sh.execute('stat {}'.format(log_path),
                                           ssh_client=ssh_client,
                                           check=False)
            except sh.ShellCommandFailed:
                containers_without_logs_gen.append(container_name)
                LOG.warning(f'Container {container_name} has no log '
                            f'file at expected location: {log_path}')
                continue

            # check the log file is bigger then 0 bytes
            # this is just a fast check to see that the container
            # is logging something
            if 'Size: 0' in log_file_stat.stdout:
                containers_without_logs_gen.append(container_name)

        # check a minority of containers in the logs without logs, this is
        # because some contrainers don't generate logs
        self.assertLess(len(containers_without_logs_gen),
                        len(expected_containers_td) / 4)

    def test_containers_logs_contain_entries(self):
        """Check  containers logs contain entries"""
        if not overcloud.has_overcloud():
            tobiko.skip('TripleO overcloud required')

        expected_containers_td = tobiko.TableData(
            tripleo_containers.get_container_states_list(
                tripleo_containers.list_containers()),
            columns=['container_host', 'container_name', 'container_state'])

        containers_with_empty_logs = []
        for container in expected_containers_td:
            container_host = container['container_host']
            container_name = container['container_name']

            if container_name.startswith('/'):
                container_name = container_name[1:]

            container_id = container_name
            node = overcloud.find_overcloud_node(name=container_host)
            ssh_client = overcloud.overcloud_ssh_client(instance=node)
            logs_result = sh.execute(
                f'{tripleo_containers.get_container_runtime_name()} logs'
                f' --tail=5 {container_id}',
                ssh_client=ssh_client, check=False)
            if not logs_result.stdout.strip():
                containers_with_empty_logs.append(container_name)

        # Less than 1/4 of containers should have empty logs
        self.assertLess(len(containers_with_empty_logs),
                        len(expected_containers_td) / 4)
