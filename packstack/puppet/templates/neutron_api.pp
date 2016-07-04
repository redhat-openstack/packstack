
class { '::neutron::server':
  database_connection => $neutron_sql_connection,
  auth_password       => $neutron_user_password,
  auth_uri            => hiera('CONFIG_KEYSTONE_PUBLIC_URL'),
  identity_uri        => hiera('CONFIG_KEYSTONE_ADMIN_URL'),
  sync_db             => true,
  enabled             => true,
  api_workers         => $service_workers,
  rpc_workers         => $service_workers,
  service_providers   => hiera_array('SERVICE_PROVIDERS')
}

# TODO: FIXME: remove this hack after upstream resolves https://bugs.launchpad.net/puppet-neutron/+bug/1474961
if hiera('CONFIG_NEUTRON_VPNAAS') == 'y' {
  ensure_resource( 'package', 'neutron-vpnaas-agent', {
    name   => 'openstack-neutron-vpnaas',
    tag    => ['openstack', 'neutron-package'],
  })
  Package['neutron-vpnaas-agent'] ~> Service<| tag == 'neutron-service' |>
}
if hiera('CONFIG_NEUTRON_FWAAS') == 'y' {
    ensure_resource( 'package', 'neutron-fwaas', {
      'name'   => 'openstack-neutron-fwaas',
      'tag'    => 'openstack'
    })
  Package['neutron-fwaas'] ~> Service<| tag == 'neutron-service' |>
}
if hiera('CONFIG_LBAAS_INSTALL') == 'y' {
  ensure_resource( 'package', 'neutron-lbaas-agent', {
    name   => 'openstack-neutron-lbaas',
    tag    => ['openstack', 'neutron-package'],
  })
  Package['neutron-lbaas-agent'] ~> Service<| tag == 'neutron-service' |>
}

file { '/etc/neutron/api-paste.ini':
  ensure  => file,
  mode    => '0640',
}

Class['::neutron::server'] -> File['/etc/neutron/api-paste.ini']

