class packstack::mariadb::services ()
{
    class { '::keystone::db::mysql':
      user          => 'keystone_admin',
      password      => hiera('CONFIG_KEYSTONE_DB_PW'),
      allowed_hosts => '%',
      charset       => 'utf8',
    }

    if hiera('CONFIG_CINDER_INSTALL') == 'y' {
         class { '::cinder::db::mysql':
           password      => hiera('CONFIG_CINDER_DB_PW'),
           host          => '%',
           allowed_hosts => '%',
           charset       => 'utf8',
         }
    }

    if hiera('CONFIG_GLANCE_INSTALL') == 'y' {
        class { '::glance::db::mysql':
          password      => hiera('CONFIG_GLANCE_DB_PW'),
          host          => '%',
          allowed_hosts => '%',
          charset       => 'utf8',
        }
    }

    if hiera('CONFIG_CEILOMETER_INSTALL') == 'y' {
        class { '::gnocchi::db::mysql':
          password      => hiera('CONFIG_GNOCCHI_DB_PW'),
          host          => '%',
          allowed_hosts => '%',
        }
    }

    if hiera('CONFIG_AODH_INSTALL') == 'y' and
       hiera('CONFIG_CEILOMETER_INSTALL') == 'y' {
        class { '::aodh::db::mysql':
          password      => hiera('CONFIG_AODH_DB_PW'),
          host          => '%',
          allowed_hosts => '%',
        }
    }

    if hiera('CONFIG_HEAT_INSTALL') == 'y' {
        class { '::heat::db::mysql':
          password      => hiera('CONFIG_HEAT_DB_PW'),
          host          => '%',
          allowed_hosts => '%',
          charset       => 'utf8',
       }
    }

    if hiera('CONFIG_MAGNUM_INSTALL') == 'y' {
        class { '::magnum::db::mysql':
          password      => hiera('CONFIG_MAGNUM_DB_PW'),
          host          => '%',
          allowed_hosts => '%',
          charset       => 'utf8',
       }
    }

    if hiera('CONFIG_IRONIC_INSTALL') == 'y' {
        class { '::ironic::db::mysql':
          password      => hiera('CONFIG_IRONIC_DB_PW'),
          host          => '%',
          allowed_hosts => '%',
          charset       => 'utf8',
        }
    }

    if hiera('CONFIG_MANILA_INSTALL') == 'y' {
        class { '::manila::db::mysql':
          password      => hiera('CONFIG_MANILA_DB_PW'),
          allowed_hosts => '%',
          charset       => 'utf8',
        }
    }

    if hiera('CONFIG_NEUTRON_INSTALL') == 'y' {
        class { '::neutron::db::mysql':
          password      => hiera('CONFIG_NEUTRON_DB_PW'),
          host          => '%',
          allowed_hosts => '%',
          dbname        => hiera('CONFIG_NEUTRON_L2_DBNAME'),
          charset       => 'utf8',
        }
    }

    if hiera('CONFIG_NOVA_INSTALL') == 'y' {
        class { '::nova::db::mysql':
          password      => hiera('CONFIG_NOVA_DB_PW'),
          host          => '%',
          allowed_hosts => '%',
          charset       => 'utf8',
        }
        class { '::nova::db::mysql_api':
          password      => hiera('CONFIG_NOVA_DB_PW'),
          host          => '%',
          allowed_hosts => '%',
          charset       => 'utf8',
        }
        class { '::nova::db::mysql_placement':
          password      => hiera('CONFIG_NOVA_DB_PW'),
          host          => '%',
          allowed_hosts => '%',
          charset       => 'utf8',
        }
    }

    if hiera('CONFIG_PANKO_INSTALL') == 'y' and
       hiera('CONFIG_CEILOMETER_INSTALL') == 'y' {
        class { '::panko::db::mysql':
          password      => hiera('CONFIG_PANKO_DB_PW'),
          host          => '%',
          allowed_hosts => '%',
        }
    }

    if hiera('CONFIG_SAHARA_INSTALL') == 'y' {
        class { '::sahara::db::mysql':
          password      => hiera('CONFIG_SAHARA_DB_PW'),
          host          => '%',
          allowed_hosts => '%',
        }

    }

    if hiera('CONFIG_TROVE_INSTALL') == 'y' {
        class { '::trove::db::mysql':
            password      => hiera('CONFIG_TROVE_DB_PW'),
            host          => '%',
            allowed_hosts => '%',
            charset       => 'utf8',
        }
    }

}
