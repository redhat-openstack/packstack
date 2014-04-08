class {'cinder::backup':
}

class {'cinder::backup::swift':
    backup_swift_url => 'http://%(CONFIG_SWIFT_PROXY)s:8080/v1/AUTH_'
}

Class['cinder::api'] ~> Service['cinder-backup']
