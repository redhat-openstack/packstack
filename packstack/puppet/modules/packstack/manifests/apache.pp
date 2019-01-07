class packstack::apache ()
{
    # Use python3 for mod_wsg in fedora
    if ($::operatingsystem == 'Fedora') or ($::osfamily == 'RedHat' and Integer.new($::operatingsystemmajrelease) > 7)  {
      class { '::apache':
        purge_configs => false,
        mod_packages => merge($::apache::params::mod_packages, {
          'wsgi' => 'python3-mod_wsgi',
        }),
        mod_libs     => merge($::apache::params::mod_libs, {
          'wsgi' => 'mod_wsgi_python3.so',
        })
      }
    }else{
      class {'::apache':
        purge_configs => false,
      }
    }

    if hiera('CONFIG_HORIZON_SSL')  == 'y' {
      ensure_packages(['mod_ssl'], {'ensure' => 'present'})
      Package['mod_ssl'] -> Class['::apache']
      apache::listen { '443': }
    }

    # Keystone port
    apache::listen { '5000': }

    if hiera('CONFIG_CEILOMETER_INSTALL') == 'y' {
      if hiera('CONFIG_CEILOMETER_SERVICE_NAME') == 'httpd' {
        # Ceilometer port
        apache::listen { '8777': }
      }
    }

    if hiera('CONFIG_AODH_INSTALL') == 'y' {
      # Aodh port
      apache::listen { '8042': }
    }

    if hiera('CONFIG_CEILOMETER_INSTALL') == 'y' {
      # Gnocchi port
      apache::listen { '8041': }
    }

    if hiera('CONFIG_PANKO_INSTALL') == 'y' {
      # Panko port
      apache::listen { '8977': }
    }
}

