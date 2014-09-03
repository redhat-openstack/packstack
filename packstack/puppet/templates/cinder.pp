cinder_config {
  "DEFAULT/glance_host": value => "%(CONFIG_STORAGE_HOST)s";
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

class {'cinder::client':
}

# Cinder::Type requires keystone credentials
Cinder::Type {
  os_password     => '%(CONFIG_CINDER_KS_PW)s',
  os_tenant_name  => "services",
  os_username     => "cinder",
  os_auth_url     => "http://%(CONFIG_CONTROLLER_HOST)s:5000/v2.0/",
}

class { 'cinder::backends':
  enabled_backends => %(CONFIG_CINDER_BACKEND)s,
}
