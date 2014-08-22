
package { 'lvm2':
  ensure => installed,
}

class {'cinder::volume::iscsi':
  iscsi_ip_address => '%(CONFIG_STORAGE_HOST)s',
  require => Package['lvm2'],
}
