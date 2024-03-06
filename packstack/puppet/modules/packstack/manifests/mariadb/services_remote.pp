class packstack::mariadb::services_remote () {
    remote_database { 'keystone':
      ensure      => 'present',
      charset     => 'utf8',
      db_host     => lookup('CONFIG_MARIADB_HOST'),
      db_user     => lookup('CONFIG_MARIADB_USER'),
      db_password => lookup('CONFIG_MARIADB_PW'),
      provider    => 'mysql',
    }

    $mariadb_keystone_noinstall_db_pw = lookup('CONFIG_KEYSTONE_DB_PW')

    remote_database_user { 'keystone_admin@%':
      password_hash => mysql_password($mariadb_keystone_noinstall_db_pw),
      db_host       => lookup('CONFIG_MARIADB_HOST'),
      db_user       => lookup('CONFIG_MARIADB_USER'),
      db_password   => lookup('CONFIG_MARIADB_PW'),
      provider      => 'mysql',
      require       => Remote_database['keystone'],
    }

    remote_database_grant { 'keystone_admin@%/keystone':
      privileges  => 'all',
      db_host     => lookup('CONFIG_MARIADB_HOST'),
      db_user     => lookup('CONFIG_MARIADB_USER'),
      db_password => lookup('CONFIG_MARIADB_PW'),
      provider    => 'mysql',
      require     => Remote_database_user['keystone_admin@%'],
    }

    if lookup('CONFIG_CINDER_INSTALL') == 'y' {
      remote_database { 'cinder':
        ensure      => 'present',
        charset     => 'utf8',
        db_host     => lookup('CONFIG_MARIADB_HOST'),
        db_user     => lookup('CONFIG_MARIADB_USER'),
        db_password => lookup('CONFIG_MARIADB_PW'),
        provider    => 'mysql',
      }

      $mariadb_cinder_noinstall_db_pw = lookup('CONFIG_CINDER_DB_PW')

      remote_database_user { 'cinder@%':
        password_hash => mysql_password($mariadb_cinder_noinstall_db_pw),
        db_host       => lookup('CONFIG_MARIADB_HOST'),
        db_user       => lookup('CONFIG_MARIADB_USER'),
        db_password   => lookup('CONFIG_MARIADB_PW'),
        provider      => 'mysql',
        require       => Remote_database['cinder'],
      }

      remote_database_grant { 'cinder@%/cinder':
        privileges  => 'all',
        db_host     => lookup('CONFIG_MARIADB_HOST'),
        db_user     => lookup('CONFIG_MARIADB_USER'),
        db_password => lookup('CONFIG_MARIADB_PW'),
        provider    => 'mysql',
        require     => Remote_database_user['cinder@%'],
      }
    }

    if lookup('CONFIG_GLANCE_INSTALL') == 'y' {
        remote_database { 'glance':
          ensure      => 'present',
          charset     => 'utf8',
          db_host     => lookup('CONFIG_MARIADB_HOST'),
          db_user     => lookup('CONFIG_MARIADB_USER'),
          db_password => lookup('CONFIG_MARIADB_PW'),
          provider    => 'mysql',
        }

        $mariadb_glance_noinstall_db_pw = lookup('CONFIG_GLANCE_DB_PW')

        remote_database_user { 'glance@%':
          password_hash => mysql_password($mariadb_glance_noinstall_db_pw),
          db_host       => lookup('CONFIG_MARIADB_HOST'),
          db_user       => lookup('CONFIG_MARIADB_USER'),
          db_password   => lookup('CONFIG_MARIADB_PW'),
          provider      => 'mysql',
          require       => Remote_database['glance'],
        }

        remote_database_grant { 'glance@%/glance':
          privileges  => 'all',
          db_host     => lookup('CONFIG_MARIADB_HOST'),
          db_user     => lookup('CONFIG_MARIADB_USER'),
          db_password => lookup('CONFIG_MARIADB_PW'),
          provider    => 'mysql',
          require     => Remote_database_user['glance@%'],
        }
    }

    if lookup('CONFIG_CEILOMETER_INSTALL') == 'y' {
        remote_database { 'gnocchi':
          ensure      => 'present',
          charset     => 'utf8',
          db_host     => lookup('CONFIG_MARIADB_HOST'),
          db_user     => lookup('CONFIG_MARIADB_USER'),
          db_password => lookup('CONFIG_MARIADB_PW'),
          provider    => 'mysql',
        }

        $gnocchi_cfg_db_pw = lookup('CONFIG_GNOCCHI_DB_PW')

        remote_database_user { 'gnocchi@%':
          password_hash => mysql_password($gnocchi_cfg_db_pw),
          db_host       => lookup('CONFIG_MARIADB_HOST'),
          db_user       => lookup('CONFIG_MARIADB_USER'),
          db_password   => lookup('CONFIG_MARIADB_PW'),
          provider      => 'mysql',
          require       => Remote_database['gnocchi'],
        }

        remote_database_grant { 'gnocchi@%/gnocchi':
          privileges  => 'all',
          db_host     => lookup('CONFIG_MARIADB_HOST'),
          db_user     => lookup('CONFIG_MARIADB_USER'),
          db_password => lookup('CONFIG_MARIADB_PW'),
          provider    => 'mysql',
          require     => Remote_database_user['gnocchi@%'],
        }
    }

    if lookup('CONFIG_AODH_INSTALL') == 'y' {
        remote_database { 'aodh':
          ensure      => 'present',
          charset     => 'utf8',
          db_host     => lookup('CONFIG_MARIADB_HOST'),
          db_user     => lookup('CONFIG_MARIADB_USER'),
          db_password => lookup('CONFIG_MARIADB_PW'),
          provider    => 'mysql',
        }

        $aodh_cfg_db_pw = lookup('CONFIG_AODH_DB_PW')

        remote_database_user { 'aodh@%':
          password_hash => mysql_password($aodh_cfg_db_pw),
          db_host       => lookup('CONFIG_MARIADB_HOST'),
          db_user       => lookup('CONFIG_MARIADB_USER'),
          db_password   => lookup('CONFIG_MARIADB_PW'),
          provider      => 'mysql',
          require       => Remote_database['aodh'],
        }

        remote_database_grant { 'aodh@%/aodh':
          privileges  => 'all',
          db_host     => lookup('CONFIG_MARIADB_HOST'),
          db_user     => lookup('CONFIG_MARIADB_USER'),
          db_password => lookup('CONFIG_MARIADB_PW'),
          provider    => 'mysql',
          require     => Remote_database_user['aodh@%'],
        }
    }

    if lookup('CONFIG_HEAT_INSTALL') == 'y' {
        remote_database { 'heat':
          ensure      => 'present',
          charset     => 'utf8',
          db_host     => lookup('CONFIG_MARIADB_HOST'),
          db_user     => lookup('CONFIG_MARIADB_USER'),
          db_password => lookup('CONFIG_MARIADB_PW'),
          provider    => 'mysql',
        }

        $mariadb_heat_noinstall_db_pw = lookup('CONFIG_HEAT_DB_PW')

        remote_database_user { 'heat@%':
          password_hash => mysql_password($mariadb_heat_noinstall_db_pw),
          db_host       => lookup('CONFIG_MARIADB_HOST'),
          db_user       => lookup('CONFIG_MARIADB_USER'),
          db_password   => lookup('CONFIG_MARIADB_PW'),
          provider      => 'mysql',
          require       => Remote_database['heat'],
        }

        remote_database_grant { 'heat@%/heat':
          privileges  => 'all',
          db_host     => lookup('CONFIG_MARIADB_HOST'),
          db_user     => lookup('CONFIG_MARIADB_USER'),
          db_password => lookup('CONFIG_MARIADB_PW'),
          provider    => 'mysql',
          require     => Remote_database_user['heat@%'],
        }
    }

    if lookup('CONFIG_MAGNUM_INSTALL') == 'y' {
        remote_database { 'magnum':
          ensure      => 'present',
          charset     => 'utf8',
          db_host     => lookup('CONFIG_MARIADB_HOST'),
          db_user     => lookup('CONFIG_MARIADB_USER'),
          db_password => lookup('CONFIG_MARIADB_PW'),
          provider    => 'mysql',
        }

        $mariadb_magnum_noinstall_db_pw = lookup('CONFIG_MAGNUM_DB_PW')

        remote_database_user { 'magnum@%':
          password_hash => mysql_password($mariadb_magnum_noinstall_db_pw),
          db_host       => lookup('CONFIG_MARIADB_HOST'),
          db_user       => lookup('CONFIG_MARIADB_USER'),
          db_password   => lookup('CONFIG_MARIADB_PW'),
          provider      => 'mysql',
          require       => Remote_database['magnum'],
        }

        remote_database_grant { 'magnum@%/magnum':
          privileges  => 'all',
          db_host     => lookup('CONFIG_MARIADB_HOST'),
          db_user     => lookup('CONFIG_MARIADB_USER'),
          db_password => lookup('CONFIG_MARIADB_PW'),
          provider    => 'mysql',
          require     => Remote_database_user['magnum@%'],
        }
    }

    if lookup('CONFIG_IRONIC_INSTALL') == 'y' {
        remote_database { 'ironic':
          ensure      => 'present',
          charset     => 'utf8',
          db_host     => lookup('CONFIG_MARIADB_HOST'),
          db_user     => lookup('CONFIG_MARIADB_USER'),
          db_password => lookup('CONFIG_MARIADB_PW'),
          provider    => 'mysql',
        }

        $mariadb_ironic_noinstall_db_pw = lookup('CONFIG_IRONIC_DB_PW')

        remote_database_user { 'ironic@%':
          password_hash => mysql_password($mariadb_ironic_noinstall_db_pw),
          db_host       => lookup('CONFIG_MARIADB_HOST'),
          db_user       => lookup('CONFIG_MARIADB_USER'),
          db_password   => lookup('CONFIG_MARIADB_PW'),
          provider      => 'mysql',
          require       => Remote_database['ironic'],
        }

        remote_database_grant { 'ironic@%/ironic':
          privileges  => 'all',
          db_host     => lookup('CONFIG_MARIADB_HOST'),
          db_user     => lookup('CONFIG_MARIADB_USER'),
          db_password => lookup('CONFIG_MARIADB_PW'),
          provider    => 'mysql',
          require     => Remote_database_user['ironic@%'],
        }
    }

    if lookup('CONFIG_MANILA_INSTALL') == 'y' {
        remote_database { 'manila':
          ensure      => 'present',
          charset     => 'utf8',
          db_host     => lookup('CONFIG_MARIADB_HOST'),
          db_user     => lookup('CONFIG_MARIADB_USER'),
          db_password => lookup('CONFIG_MARIADB_PW'),
          provider    => 'mysql',
        }

        $mariadb_manila_noinstall_db_pw = lookup('CONFIG_MANILA_DB_PW')

        remote_database_user { 'manila@%':
          password_hash => mysql_password($mariadb_manila_noinstall_db_pw),
          db_host       => lookup('CONFIG_MARIADB_HOST'),
          db_user       => lookup('CONFIG_MARIADB_USER'),
          db_password   => lookup('CONFIG_MARIADB_PW'),
          provider      => 'mysql',
          require       => Remote_database['manila'],
        }

        remote_database_grant { 'manila@%/manila':
          privileges  => 'all',
          db_host     => lookup('CONFIG_MARIADB_HOST'),
          db_user     => lookup('CONFIG_MARIADB_USER'),
          db_password => lookup('CONFIG_MARIADB_PW'),
          provider    => 'mysql',
          require     => Remote_database_user['manila@%'],
        }
    }

    if lookup('CONFIG_NEUTRON_INSTALL') == 'y' {
        $mariadb_neutron_noinstall_db_pw     = lookup('CONFIG_NEUTRON_DB_PW')
        $mariadb_neutron_noinstall_l2_dbname = lookup('CONFIG_NEUTRON_L2_DBNAME')

        remote_database { $mariadb_neutron_noinstall_l2_dbname:
          ensure      => present,
          charset     => 'utf8',
          db_host     => lookup('CONFIG_MARIADB_HOST'),
          db_user     => lookup('CONFIG_MARIADB_USER'),
          db_password => lookup('CONFIG_MARIADB_PW'),
          provider    => 'mysql',
        }

        remote_database_user { 'neutron@%':
          password_hash => mysql_password($mariadb_neutron_noinstall_db_pw),
          db_host       => lookup('CONFIG_MARIADB_HOST'),
          db_user       => lookup('CONFIG_MARIADB_USER'),
          db_password   => lookup('CONFIG_MARIADB_PW'),
          provider      => 'mysql',
          require       => Remote_database[$mariadb_neutron_noinstall_l2_dbname],
        }

        remote_database_grant { "neutron@%/${mariadb_neutron_noinstall_l2_dbname}":
          privileges  => 'all',
          db_host     => lookup('CONFIG_MARIADB_HOST'),
          db_user     => lookup('CONFIG_MARIADB_USER'),
          db_password => lookup('CONFIG_MARIADB_PW'),
          provider    => 'mysql',
          require     => Remote_database_user['neutron@%'],
        }
    }

    if lookup('CONFIG_NOVA_INSTALL') == 'y' {
        remote_database { 'nova':
          ensure      => 'present',
          charset     => 'utf8',
          db_host     => lookup('CONFIG_MARIADB_HOST'),
          db_user     => lookup('CONFIG_MARIADB_USER'),
          db_password => lookup('CONFIG_MARIADB_PW'),
          provider    => 'mysql',
        }

        $mariadb_nova_noinstall_db_pw = lookup('CONFIG_NOVA_DB_PW')

        remote_database_user { 'nova@%':
          password_hash => mysql_password($mariadb_nova_noinstall_db_pw),
          db_host       => lookup('CONFIG_MARIADB_HOST'),
          db_user       => lookup('CONFIG_MARIADB_USER'),
          db_password   => lookup('CONFIG_MARIADB_PW'),
          provider      => 'mysql',
          require       => Remote_database['nova'],
        }

        remote_database_grant { 'nova@%/nova':
          privileges  => 'all',
          db_host     => lookup('CONFIG_MARIADB_HOST'),
          db_user     => lookup('CONFIG_MARIADB_USER'),
          db_password => lookup('CONFIG_MARIADB_PW'),
          provider    => 'mysql',
          require     => Remote_database_user['nova@%'],
        }

        remote_database { 'nova_api':
          ensure      => 'present',
          charset     => 'utf8',
          db_host     => lookup('CONFIG_MARIADB_HOST'),
          db_user     => lookup('CONFIG_MARIADB_USER'),
          db_password => lookup('CONFIG_MARIADB_PW'),
          provider    => 'mysql',
        }

        remote_database_user { 'nova_api@%':
          password_hash => mysql_password($mariadb_nova_noinstall_db_pw),
          db_host       => lookup('CONFIG_MARIADB_HOST'),
          db_user       => lookup('CONFIG_MARIADB_USER'),
          db_password   => lookup('CONFIG_MARIADB_PW'),
          provider      => 'mysql',
          require       => Remote_database['nova_api'],
        }

        remote_database_grant { 'nova_api@%/nova_api':
          privileges  => 'all',
          db_host     => lookup('CONFIG_MARIADB_HOST'),
          db_user     => lookup('CONFIG_MARIADB_USER'),
          db_password => lookup('CONFIG_MARIADB_PW'),
          provider    => 'mysql',
          require     => Remote_database_user['nova_api@%'],
        }

        remote_database { 'placement':
          ensure      => 'present',
          charset     => 'utf8',
          db_host     => lookup('CONFIG_MARIADB_HOST'),
          db_user     => lookup('CONFIG_MARIADB_USER'),
          db_password => lookup('CONFIG_MARIADB_PW'),
          provider    => 'mysql',
        }

        remote_database_user { 'placement@%':
          password_hash => mysql_password($mariadb_nova_noinstall_db_pw),
          db_host       => lookup('CONFIG_MARIADB_HOST'),
          db_user       => lookup('CONFIG_MARIADB_USER'),
          db_password   => lookup('CONFIG_MARIADB_PW'),
          provider      => 'mysql',
          require       => Remote_database['placement'],
        }

        remote_database_grant { 'placement@%/placement':
          privileges  => 'all',
          db_host     => lookup('CONFIG_MARIADB_HOST'),
          db_user     => lookup('CONFIG_MARIADB_USER'),
          db_password => lookup('CONFIG_MARIADB_PW'),
          provider    => 'mysql',
          require     => Remote_database_user['placement@%'],
        }

        remote_database { 'nova_cell0':
          ensure      => 'present',
          charset     => 'utf8',
          db_host     => lookup('CONFIG_MARIADB_HOST'),
          db_user     => lookup('CONFIG_MARIADB_USER'),
          db_password => lookup('CONFIG_MARIADB_PW'),
          provider    => 'mysql',
        }

        remote_database_grant { 'nova@%/nova_cell0':
          privileges  => 'all',
          db_host     => lookup('CONFIG_MARIADB_HOST'),
          db_user     => lookup('CONFIG_MARIADB_USER'),
          db_password => lookup('CONFIG_MARIADB_PW'),
          provider    => 'mysql',
          require     => [ Remote_database_user['nova@%'],
                          Remote_database['nova_cell0'] ],
        }

    }

    if lookup('CONFIG_TROVE_INSTALL') == 'y' {
        remote_database { 'trove':
          ensure      => 'present',
          charset     => 'utf8',
          db_host     => lookup('CONFIG_MARIADB_HOST'),
          db_user     => lookup('CONFIG_MARIADB_USER'),
          db_password => lookup('CONFIG_MARIADB_PW'),
          provider    => 'mysql',
        }

        $trove_cfg_trove_db_pw = lookup('CONFIG_TROVE_DB_PW')

        remote_database_user { 'trove@%':
          password_hash => mysql_password($trove_cfg_trove_db_pw),
          db_host       => lookup('CONFIG_MARIADB_HOST'),
          db_user       => lookup('CONFIG_MARIADB_USER'),
          db_password   => lookup('CONFIG_MARIADB_PW'),
          provider      => 'mysql',
          require       => Remote_database['trove'],
        }

        remote_database_grant { 'trove@%/trove':
          privileges  => 'all',
          db_host     => lookup('CONFIG_MARIADB_HOST'),
          db_user     => lookup('CONFIG_MARIADB_USER'),
          db_password => lookup('CONFIG_MARIADB_PW'),
          provider    => 'mysql',
          require     => Remote_database_user['trove@%'],
        }
    }

}
