class packstack::mariadb::services ()
{
    class { 'keystone::db::mysql':
      user          => 'keystone_admin',
      password      => lookup('CONFIG_KEYSTONE_DB_PW'),
      allowed_hosts => '%',
      charset       => 'utf8',
    }

    if lookup('CONFIG_CINDER_INSTALL') == 'y' {
      class { 'cinder::db::mysql':
        password      => lookup('CONFIG_CINDER_DB_PW'),
        host          => '%',
        allowed_hosts => '%',
        charset       => 'utf8',
      }
    }

    if lookup('CONFIG_GLANCE_INSTALL') == 'y' {
        class { 'glance::db::mysql':
          password      => lookup('CONFIG_GLANCE_DB_PW'),
          host          => '%',
          allowed_hosts => '%',
          charset       => 'utf8',
        }
    }

    if lookup('CONFIG_CEILOMETER_INSTALL') == 'y' {
        class { 'gnocchi::db::mysql':
          password      => lookup('CONFIG_GNOCCHI_DB_PW'),
          host          => '%',
          allowed_hosts => '%',
        }
    }

    if lookup('CONFIG_AODH_INSTALL') == 'y' and
      lookup('CONFIG_CEILOMETER_INSTALL') == 'y' {
        class { 'aodh::db::mysql':
          password      => lookup('CONFIG_AODH_DB_PW'),
          host          => '%',
          allowed_hosts => '%',
        }
    }

    if lookup('CONFIG_HEAT_INSTALL') == 'y' {
      class { 'heat::db::mysql':
        password      => lookup('CONFIG_HEAT_DB_PW'),
        host          => '%',
        allowed_hosts => '%',
        charset       => 'utf8',
      }
    }

    if lookup('CONFIG_MAGNUM_INSTALL') == 'y' {
      class { 'magnum::db::mysql':
        password      => lookup('CONFIG_MAGNUM_DB_PW'),
        host          => '%',
        allowed_hosts => '%',
        charset       => 'utf8',
      }
    }

    if lookup('CONFIG_IRONIC_INSTALL') == 'y' {
      class { 'ironic::db::mysql':
        password      => lookup('CONFIG_IRONIC_DB_PW'),
        host          => '%',
        allowed_hosts => '%',
        charset       => 'utf8',
      }
    }

    if lookup('CONFIG_MANILA_INSTALL') == 'y' {
        class { 'manila::db::mysql':
          password      => lookup('CONFIG_MANILA_DB_PW'),
          allowed_hosts => '%',
          charset       => 'utf8',
        }
    }

    if lookup('CONFIG_NEUTRON_INSTALL') == 'y' {
        class { 'neutron::db::mysql':
          password      => lookup('CONFIG_NEUTRON_DB_PW'),
          host          => '%',
          allowed_hosts => '%',
          dbname        => lookup('CONFIG_NEUTRON_L2_DBNAME'),
          charset       => 'utf8',
        }
    }

    if lookup('CONFIG_NOVA_INSTALL') == 'y' {
        class { 'nova::db::mysql':
          password      => lookup('CONFIG_NOVA_DB_PW'),
          host          => '%',
          allowed_hosts => '%',
          charset       => 'utf8',
        }
        class { 'nova::db::mysql_api':
          password      => lookup('CONFIG_NOVA_DB_PW'),
          host          => '%',
          allowed_hosts => '%',
          charset       => 'utf8',
        }
        class { 'placement::db::mysql':
          password      => lookup('CONFIG_NOVA_DB_PW'),
          host          => '%',
          allowed_hosts => '%',
          charset       => 'utf8',
        }
    }

    if lookup('CONFIG_TROVE_INSTALL') == 'y' {
        class { 'trove::db::mysql':
            password      => lookup('CONFIG_TROVE_DB_PW'),
            host          => '%',
            allowed_hosts => '%',
            charset       => 'utf8',
        }
    }

}
