class packstack::neutron::api ()
{
    create_resources(packstack::firewall, lookup('FIREWALL_NEUTRON_SERVER_RULES', undef, undef, {}))

    $neutron_db_host         = lookup('CONFIG_MARIADB_HOST_URL')
    $neutron_db_name         = lookup('CONFIG_NEUTRON_L2_DBNAME')
    $neutron_db_user         = 'neutron'
    $neutron_db_password     = lookup('CONFIG_NEUTRON_DB_PW')
    $neutron_sql_connection  = "mysql+pymysql://${neutron_db_user}:${neutron_db_password}@${neutron_db_host}/${neutron_db_name}"
    $neutron_user_password   = lookup('CONFIG_NEUTRON_KS_PW')
    $neutron_vpnaas_enabled  = str2bool(lookup('CONFIG_NEUTRON_VPNAAS'))

    class { 'neutron::keystone::authtoken':
      password             => $neutron_user_password,
      www_authenticate_uri => lookup('CONFIG_KEYSTONE_PUBLIC_URL_VERSIONLESS'),
      auth_url             => lookup('CONFIG_KEYSTONE_ADMIN_URL'),
    }

    class { 'neutron::db':
      database_connection   => $neutron_sql_connection,
    }

    class { 'neutron::server':
      sync_db               => true,
      enabled               => true,
      api_workers           => lookup('CONFIG_SERVICE_WORKERS'),
      rpc_workers           => lookup('CONFIG_SERVICE_WORKERS'),
      service_providers     => lookup('SERVICE_PROVIDERS', { merge => 'unique' }),
    }

    file { '/etc/neutron/api-paste.ini':
      ensure => file,
      mode   => '0640',
    }

    if $neutron_vpnaas_enabled {
      class { 'neutron::services::vpnaas': }
    }

    Class['::neutron::server'] -> File['/etc/neutron/api-paste.ini']
}
