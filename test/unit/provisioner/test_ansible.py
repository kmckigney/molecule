#  Copyright (c) 2015-2017 Cisco Systems, Inc.
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to
#  deal in the Software without restriction, including without limitation the
#  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#  sell copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#  DEALINGS IN THE SOFTWARE.

import os

import pytest

from molecule import config
from molecule import util
from molecule.provisioner import ansible


@pytest.fixture
def ansible_data():
    return {
        'provisioner': {
            'name': 'ansible',
            'config_options': {
                'defaults': {
                    'foo': 'bar'
                },
            },
            'options': {
                'foo': 'bar'
            },
            'host_vars': {
                'instance-1': [{
                    'foo': 'bar'
                }],
            },
            'group_vars': {
                'example_group1': [{
                    'foo': 'bar'
                }],
                'example_group2': [{
                    'foo': 'bar'
                }],
            },
        }
    }


@pytest.fixture
def molecule_provisioner_section_data():
    return {
        'provisioner': {
            'name': 'ansible',
            'config_options': {
                'defaults': {
                    'foo': 'bar'
                },
            },
            'options': {
                'foo': 'bar'
            },
            'env': {
                'foo': 'bar'
            },
            'host_vars': {
                'instance-1': [{
                    'foo': 'bar'
                }],
            },
            'group_vars': {
                'example_group1': [{
                    'foo': 'bar'
                }],
                'example_group2': [{
                    'foo': 'bar'
                }],
            }
        },
    }


@pytest.fixture
def ansible_instance(molecule_provisioner_section_data, config_instance):
    config_instance.config.update(molecule_provisioner_section_data)

    return ansible.Ansible(config_instance)


def test_config_private_member(ansible_instance):
    assert isinstance(ansible_instance._config, config.Config)


def test_default_config_options_property(ansible_instance):
    libraries_directory = ansible_instance._get_libraries_directory()
    filter_plugins_directory = ansible_instance._get_filter_plugin_directory()
    x = {
        'defaults': {
            'ansible_managed':
            'Ansible managed: Do NOT edit this file manually!',
            'retry_files_enabled': False,
            'host_key_checking': False,
            'roles_path': '../../../../:$ANSIBLE_ROLES_PATH',
            'library': '{}:$ANSIBLE_LIBRARY'.format(libraries_directory),
            'filter_plugins':
            '{}:$ANSIBLE_FILTER_PLUGINS'.format(filter_plugins_directory),
        },
        'ssh_connection': {
            'ssh_args': '-o UserKnownHostsFile=/dev/null'
        },
    }

    assert x == ansible_instance.default_config_options


def test_default_options_property(ansible_instance):
    assert {} == ansible_instance.default_options


def test_default_env_property(ansible_instance):
    x = ansible_instance._config.provisioner.config_file

    assert x == ansible_instance.default_env['ANSIBLE_CONFIG']


def test_name_property(ansible_instance):
    assert 'ansible' == ansible_instance.name


def test_config_options_property(ansible_instance):
    libraries_directory = ansible_instance._get_libraries_directory()
    filter_plugins_directory = ansible_instance._get_filter_plugin_directory()
    x = {
        'defaults': {
            'ansible_managed':
            'Ansible managed: Do NOT edit this file manually!',
            'retry_files_enabled': False,
            'host_key_checking': False,
            'roles_path': '../../../../:$ANSIBLE_ROLES_PATH',
            'library': '{}:$ANSIBLE_LIBRARY'.format(libraries_directory),
            'filter_plugins':
            '{}:$ANSIBLE_FILTER_PLUGINS'.format(filter_plugins_directory),
            'foo': 'bar'
        },
        'ssh_connection': {
            'ssh_args': '-o UserKnownHostsFile=/dev/null'
        },
    }

    assert x == ansible_instance.config_options


def test_options_property(ansible_instance):
    x = {'foo': 'bar'}

    assert x == ansible_instance.options


def test_options_property_handles_cli_args(ansible_instance):
    ansible_instance._config.args = {'debug': True}

    assert ansible_instance.options['debug']


def test_env_property(ansible_instance):
    x = ansible_instance._config.provisioner.config_file

    assert x == ansible_instance.env['ANSIBLE_CONFIG']
    assert 'bar' == ansible_instance.env['foo']


def test_host_vars_property(ansible_instance):
    x = {'instance-1': [{'foo': 'bar'}]}

    assert x == ansible_instance.host_vars


def test_group_vars_property(ansible_instance):
    x = {
        'example_group1': [{
            'foo': 'bar'
        }],
        'example_group2': [{
            'foo': 'bar'
        }]
    }

    assert x == ansible_instance.group_vars


def test_inventory_property(ansible_instance):
    x = {
        'ungrouped': {
            'vars': {
                'molecule_file': ansible_instance._config.molecule_file,
                'molecule_instance_config':
                ansible_instance._config.driver.instance_config,
                'molecule_inventory_file':
                ansible_instance._config.provisioner.inventory_file,
                'molecule_scenario_directory':
                ansible_instance._config.scenario.directory,
            }
        },
        'bar': {
            'hosts': {
                'instance-1-default': {
                    'ansible_connection': 'docker'
                }
            },
            'children': {
                'child1': {
                    'hosts': {
                        'instance-1-default': {
                            'ansible_connection': 'docker'
                        }
                    }
                }
            }
        },
        'foo': {
            'hosts': {
                'instance-1-default': {
                    'ansible_connection': 'docker'
                },
                'instance-2-default': {
                    'ansible_connection': 'docker'
                }
            },
            'children': {
                'child1': {
                    'hosts': {
                        'instance-1-default': {
                            'ansible_connection': 'docker'
                        }
                    }
                },
                'child2': {
                    'hosts': {
                        'instance-2-default': {
                            'ansible_connection': 'docker'
                        }
                    }
                }
            }
        },
        'baz': {
            'hosts': {
                'instance-2-default': {
                    'ansible_connection': 'docker'
                }
            },
            'children': {
                'child2': {
                    'hosts': {
                        'instance-2-default': {
                            'ansible_connection': 'docker'
                        }
                    }
                }
            }
        }
    }

    assert x == ansible_instance.inventory


def test_inventory_property_handles_missing_groups(temp_dir, ansible_instance):
    platforms = [{'name': 'instance-1'}, {'name': 'instance-2'}]
    ansible_instance._config.config['platforms'] = platforms

    x = {
        'ungrouped': {
            'hosts': {
                'instance-1-default': {
                    'ansible_connection': 'docker'
                },
                'instance-2-default': {
                    'ansible_connection': 'docker'
                }
            },
            'vars': {
                'molecule_file': ansible_instance._config.molecule_file,
                'molecule_instance_config':
                ansible_instance._config.driver.instance_config,
                'molecule_inventory_file':
                ansible_instance._config.provisioner.inventory_file,
                'molecule_scenario_directory':
                ansible_instance._config.scenario.directory,
            }
        }
    }

    assert x == ansible_instance.inventory


def test_inventory_file_property(ansible_instance):
    x = os.path.join(ansible_instance._config.ephemeral_directory,
                     'ansible_inventory.yml')

    assert x == ansible_instance.inventory_file


def test_config_file_property(ansible_instance):
    x = os.path.join(ansible_instance._config.ephemeral_directory,
                     'ansible.cfg')

    assert x == ansible_instance.config_file


def test_add_or_update_vars(ansible_instance):
    ephemeral_directory = ansible_instance._config.ephemeral_directory

    host_vars_directory = os.path.join(ephemeral_directory, 'host_vars')
    host_vars = os.path.join(host_vars_directory, 'instance-1-default')

    ansible_instance.add_or_update_vars('host_vars')
    assert os.path.isdir(host_vars_directory)
    assert os.path.isfile(host_vars)

    group_vars_directory = os.path.join(ephemeral_directory, 'group_vars')
    group_vars_1 = os.path.join(group_vars_directory, 'example_group1')
    group_vars_2 = os.path.join(group_vars_directory, 'example_group2')

    ansible_instance.add_or_update_vars('group_vars')
    assert os.path.isdir(group_vars_directory)
    assert os.path.isfile(group_vars_1)
    assert os.path.isfile(group_vars_2)


def test_add_or_update_vars_does_not_create_vars(ansible_instance):
    ansible_instance._config.config['provisioner']['host_vars'] = {}
    ansible_instance._config.config['provisioner']['group_vars'] = {}
    ephemeral_directory = ansible_instance._config.ephemeral_directory

    host_vars_directory = os.path.join(ephemeral_directory, 'host_vars')
    group_vars_directory = os.path.join(ephemeral_directory, 'group_vars')

    ansible_instance.add_or_update_vars('host_vars')
    ansible_instance.add_or_update_vars('group_vars')

    assert not os.path.isdir(host_vars_directory)
    assert not os.path.isdir(group_vars_directory)


def test_converge(ansible_instance, mocker, patched_ansible_playbook):
    result = ansible_instance.converge('playbook')

    inventory_file = ansible_instance._config.provisioner.inventory_file
    patched_ansible_playbook.assert_called_once_with(
        inventory_file, 'playbook', ansible_instance._config)
    assert result == 'patched-ansible-playbook-stdout'

    patched_ansible_playbook.return_value.execute.assert_called_once_with()


def test_syntax(ansible_instance, mocker, patched_ansible_playbook):
    ansible_instance.syntax('playbook')

    inventory_file = ansible_instance._config.provisioner.inventory_file
    patched_ansible_playbook.assert_called_once_with(
        inventory_file, 'playbook', ansible_instance._config)
    patched_ansible_playbook.return_value.add_cli_arg.assert_called_once_with(
        'syntax-check', True)
    patched_ansible_playbook.return_value.execute.assert_called_once_with()


def test_check(ansible_instance, mocker, patched_ansible_playbook):
    ansible_instance.check('playbook')

    inventory_file = ansible_instance._config.provisioner.inventory_file
    patched_ansible_playbook.assert_called_once_with(
        inventory_file, 'playbook', ansible_instance._config)
    patched_ansible_playbook.return_value.add_cli_arg.assert_called_once_with(
        'check', True)
    patched_ansible_playbook.return_value.execute.assert_called_once_with()


def test_write_inventory(temp_dir, ansible_instance):
    ansible_instance.write_inventory()

    assert os.path.isfile(ansible_instance.inventory_file)

    data = util.safe_load_file(ansible_instance.inventory_file)

    x = {
        'ungrouped': {
            'vars': {
                'molecule_file': ansible_instance._config.molecule_file,
                'molecule_instance_config':
                ansible_instance._config.driver.instance_config,
                'molecule_inventory_file':
                ansible_instance._config.provisioner.inventory_file,
                'molecule_scenario_directory':
                ansible_instance._config.scenario.directory,
            }
        },
        'bar': {
            'hosts': {
                'instance-1-default': {
                    'ansible_connection': 'docker'
                }
            },
            'children': {
                'child1': {
                    'hosts': {
                        'instance-1-default': {
                            'ansible_connection': 'docker'
                        }
                    }
                }
            }
        },
        'foo': {
            'hosts': {
                'instance-1-default': {
                    'ansible_connection': 'docker'
                },
                'instance-2-default': {
                    'ansible_connection': 'docker'
                }
            },
            'children': {
                'child1': {
                    'hosts': {
                        'instance-1-default': {
                            'ansible_connection': 'docker'
                        }
                    }
                },
                'child2': {
                    'hosts': {
                        'instance-2-default': {
                            'ansible_connection': 'docker'
                        }
                    }
                }
            }
        },
        'baz': {
            'hosts': {
                'instance-2-default': {
                    'ansible_connection': 'docker'
                }
            },
            'children': {
                'child2': {
                    'hosts': {
                        'instance-2-default': {
                            'ansible_connection': 'docker'
                        }
                    }
                }
            }
        }
    }

    assert x == data


def test_write_config(temp_dir, ansible_instance):
    ansible_instance.write_config()

    assert os.path.isfile(ansible_instance.config_file)


def test_verify_inventory(ansible_instance):
    ansible_instance._verify_inventory()


def test_verify_inventory_raises_when_missing_hosts(
        temp_dir, patched_print_error, ansible_instance):
    ansible_instance._config.config['platforms'] = []
    with pytest.raises(SystemExit) as e:
        ansible_instance._verify_inventory()

    assert 1 == e.value.code

    msg = "Instances missing from the 'platform' section of molecule.yml."
    patched_print_error.assert_called_once_with(msg)


def test_vivify(ansible_instance):
    d = ansible_instance._vivify()
    d['bar']['baz'] = 'qux'

    assert 'qux' == str(d['bar']['baz'])


def test_get_plugin_directory(ansible_instance):
    result = ansible_instance._get_plugin_directory()
    parts = pytest.helpers.os_split(result)

    assert ('molecule', 'provisioner', 'ansible', 'plugins') == parts[-4:]


def test_get_libraries_directory(ansible_instance):
    result = ansible_instance._get_libraries_directory()
    parts = pytest.helpers.os_split(result)
    x = ('molecule', 'provisioner', 'ansible', 'plugins', 'libraries')

    assert x == parts[-5:]


def test_get_filter_plugin_directory(ansible_instance):
    result = ansible_instance._get_filter_plugin_directory()
    parts = pytest.helpers.os_split(result)
    x = ('molecule', 'provisioner', 'ansible', 'plugins', 'filters')

    assert x == parts[-5:]
