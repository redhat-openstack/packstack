$trove_qpid_cfg_trove_db_pw = hiera('CONFIG_TROVE_DB_PW')
$trove_qpid_cfg_mariadb_host = hiera('CONFIG_MARIADB_HOST')
$trove_qpid_cfg_controller_host = hiera('CONFIG_CONTROLLER_HOST')

class { '::trove':
  rpc_backend                  => 'trove.openstack.common.rpc.impl_qpid',
  qpid_hostname                => hiera('CONFIG_AMQP_HOST'),
  qpid_port                    => hiera('CONFIG_AMQP_CLIENTS_PORT'),
  qpid_protocol                => hiera('CONFIG_AMQP_PROTOCOL'),
  qpid_username                => hiera('CONFIG_AMQP_AUTH_USER'),
  qpid_password                => hiera('CONFIG_AMQP_AUTH_PASSWORD'),
  database_connection          => "mysql://trove:${trove_qpid_cfg_trove_db_pw}@${trove_qpid_cfg_mariadb_host}/trove",
  nova_proxy_admin_user        => hiera('CONFIG_TROVE_NOVA_USER'),
  nova_proxy_admin_tenant_name => hiera('CONFIG_TROVE_NOVA_TENANT'),
  nova_proxy_admin_pass        => hiera('CONFIG_TROVE_NOVA_PW'),
  nova_compute_url             => "http://${trove_qpid_cfg_controller_host}:8774/v2",
  cinder_url                   => "http://${trove_qpid_cfg_controller_host}:8776/v1",
  swift_url                    => "http://${trove_qpid_cfg_controller_host}:8080/v1/AUTH_",
  use_neutron                  => hiera('CONFIG_NEUTRON_INSTALL'),
}

