class packstack::neutron::api ()
{
    create_resources(packstack::firewall, lookup('FIREWALL_NEUTRON_SERVER_RULES', undef, undef, {}))

    $neutron_vpnaas_enabled = str2bool(lookup('CONFIG_NEUTRON_VPNAAS'))

    class { 'neutron::keystone::authtoken':
      password             => lookup('CONFIG_NEUTRON_KS_PW'),
      www_authenticate_uri => lookup('CONFIG_KEYSTONE_PUBLIC_URL_VERSIONLESS'),
      auth_url             => lookup('CONFIG_KEYSTONE_ADMIN_URL'),
    }

    class { 'neutron::db':
      database_connection => os_database_connection({
        'dialect'  => 'mysql+pymysql',
        'host'     => lookup('CONFIG_MARIADB_HOST_URL'),
        'username' => 'neutron',
        'password' => lookup('CONFIG_NEUTRON_DB_PW'),
        'database' => lookup('CONFIG_NEUTRON_L2_DBNAME'),
      })
    }

    class { 'neutron::server':
      sync_db               => true,
      enabled               => true,
      api_workers           => lookup('CONFIG_SERVICE_WORKERS'),
      rpc_workers           => lookup('CONFIG_SERVICE_WORKERS'),
      service_providers     => lookup('SERVICE_PROVIDERS', { merge => 'unique' }),
    }

    if $neutron_vpnaas_enabled {
      class { 'neutron::services::vpnaas': }
    }
}
