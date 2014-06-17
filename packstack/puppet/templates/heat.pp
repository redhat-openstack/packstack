
class { 'heat::api':
}

class { 'heat::engine':
  heat_metadata_server_url      => 'http://%(CONFIG_CONTROLLER_HOST)s:8000',
  heat_waitcondition_server_url => 'http://%(CONFIG_CONTROLLER_HOST)s:8000/v1/waitcondition',
  heat_watch_server_url         => 'http://%(CONFIG_CONTROLLER_HOST)s:8003',
  auth_encryption_key           => '%(CONFIG_HEAT_AUTH_ENC_KEY)s',
}

class { 'heat::keystone::domain':
  auth_url          => 'http://%(CONFIG_CONTROLLER_HOST)s:35357/v2.0',
  keystone_admin    => 'admin',
  keystone_password => '%(CONFIG_KEYSTONE_ADMIN_PW)s',
  keystone_tenant   => 'admin',
  domain_name       => '%(CONFIG_HEAT_DOMAIN)s',
  domain_admin      => '%(CONFIG_HEAT_DOMAIN_ADMIN)s',
  domain_password   => '%(CONFIG_HEAT_DOMAIN_PASSWORD)s',
}

