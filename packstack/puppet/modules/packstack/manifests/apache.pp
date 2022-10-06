class packstack::apache ()
{
    # Use python3 for mod_wsg in fedora
    if ($::operatingsystem == 'Fedora') or ($::osfamily == 'RedHat' and Integer.new($::operatingsystemmajrelease) > 7)  {
      class { 'apache':
        mod_packages  => merge($::apache::params::mod_packages, {
          'wsgi' => 'python3-mod_wsgi',
        }),
        mod_libs      => merge($::apache::params::mod_libs, {
          'wsgi' => 'mod_wsgi_python3.so',
        })
      }
    }else{
      class { 'apache':
      }
    }

    if lookup('CONFIG_HORIZON_SSL') == 'y' {
      ensure_packages(['mod_ssl'], {'ensure' => 'present'})
      Package['mod_ssl'] -> Class['apache']
    }
}

