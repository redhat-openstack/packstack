class packstack::neutron::api ()
{
    create_resources(packstack::firewall, hiera('FIREWALL_NEUTRON_SERVER_RULES', {}))

    $neutron_db_host         = hiera('CONFIG_MARIADB_HOST_URL')
    $neutron_db_name         = hiera('CONFIG_NEUTRON_L2_DBNAME')
    $neutron_db_user         = 'neutron'
    $neutron_db_password     = hiera('CONFIG_NEUTRON_DB_PW')
    $neutron_sql_connection  = "mysql+pymysql://${neutron_db_user}:${neutron_db_password}@${neutron_db_host}/${neutron_db_name}"
    $neutron_user_password   = hiera('CONFIG_NEUTRON_KS_PW')

    class { '::neutron::server':
      database_connection => $neutron_sql_connection,
      auth_password       => $neutron_user_password,
      auth_uri            => hiera('CONFIG_KEYSTONE_PUBLIC_URL'),
      identity_uri        => hiera('CONFIG_KEYSTONE_ADMIN_URL'),
      sync_db             => true,
      enabled             => true,
      api_workers         => hiera('CONFIG_SERVICE_WORKERS'),
      rpc_workers         => hiera('CONFIG_SERVICE_WORKERS'),
      service_providers   => hiera_array('SERVICE_PROVIDERS'),
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
}
