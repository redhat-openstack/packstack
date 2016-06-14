class packstack::apache ()
{
    include ::apache

    if hiera('CONFIG_HORIZON_SSL')  == 'y' {
      ensure_packages(['mod_ssl'], {'ensure' => 'present'})
      Package['mod_ssl'] -> Class['::apache']
      apache::listen { '443': }
    }

    # Keystone port
    apache::listen { '5000': }
    # Keystone admin port
    apache::listen { '35357': }

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

    if hiera('CONFIG_GNOCCHI_INSTALL') == 'y' {
      # Gnocchi port
      apache::listen { '8041': }
    }
}

