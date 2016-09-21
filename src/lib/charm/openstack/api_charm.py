import socket
import subprocess

import charmhelpers.core.hookenv as hookenv
import charms_openstack.charm
import charms_openstack.ip as os_ip

# import charms_openstack.sdn.odl as odl
# import charms_openstack.sdn.ovs as ovs


class {{ charm_class }}(charms_openstack.charm.HAOpenStackCharm):

    # Internal name of charm
    service_name = name = '{{ metadata.package }}'

    # First release supported
    release = '{{ release }}'

    # List of packages to install for this charm
    packages = {{ packages }}

    api_ports = {
        '{{ api_service }}': {
            os_ip.PUBLIC: {{ service_port }},
            os_ip.ADMIN: {{ service_port }},
            os_ip.INTERNAL: {{ service_port }},
        }
    }

    service_type = '{{ service_name }}'
    default_service = '{{ api_service }}'
    services = {{ all_services }}

    # Note that the hsm interface is optional - defined in config.yaml
    required_relations = ['shared-db', 'amqp', 'identity-service']

    restart_map = {{ restart_map }}

    ha_resources = ['vips', 'haproxy']

{% if db_sync_commands|length > 1 %}

    def db_sync(self):
        """Perform a database sync using the command defined in the
        self.sync_cmd attribute. The services defined in self.services are
        restarted after the database sync.
        """
        if not self.db_sync_done() and hookenv.is_leader():
{% for cmd in db_sync_commands %}
            subprocess.check_call({{ cmd }})
{% endfor %}    
            hookenv.leader_set({'db-sync-done': True})
            # Restart services immediately after db sync as
            # render_domain_config needs a working system
            self.restart_all()
{%- else %}
    sync_cmd = {{ db_sync_command }}
{%- endif %}

    def get_amqp_credentials(self):
        return ('{{ service_name }}', '{{ service_name }}')

    def get_database_setup(self):
        return [{
            'database': '{{ service_name }}',
            'username': '{{ service_name }}',
            'hostname': hookenv.unit_private_ip() },]
