cinder_config {
    "DEFAULT/glance_host": value => "%(CONFIG_CONTROLLER_HOST)s";
}

package {'python-keystone':
    notify => Class['cinder::api'],
}

class {'cinder::api':
    keystone_password => '%(CONFIG_CINDER_KS_PW)s',
    keystone_tenant => "services",
    keystone_user => "cinder",
    keystone_auth_host => "%(CONFIG_CONTROLLER_HOST)s",
}

class {'cinder::scheduler':
}

class {'cinder::volume':
}
