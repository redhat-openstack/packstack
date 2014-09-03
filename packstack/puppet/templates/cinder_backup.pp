class { 'cinder::backup':
}

class { 'cinder::backup::swift':
  backup_swift_url => 'http://%(CONFIG_CONTROLLER_HOST)s:8080/v1/AUTH_'
}

Class['cinder::api'] ~> Service['cinder-backup']
