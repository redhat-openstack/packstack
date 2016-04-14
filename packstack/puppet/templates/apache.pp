include ::apache

if hiera('CONFIG_HORIZON_SSL')  == 'y' {
  package { 'mod_ssl':
    ensure => installed,
  }

  Package['mod_ssl'] -> Class['::apache']
}
