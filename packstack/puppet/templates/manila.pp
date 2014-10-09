manila_config {
  'DEFAULT/glance_host': value => hiera('CONFIG_CONTROLLER_HOST');
}

package { 'python-keystone':
  notify => Class['manila::api'],
}

class { 'manila::api':
  keystone_password  => hiera('CONFIG_MANILA_KS_PW'),
  keystone_tenant    => 'services',
  keystone_user      => 'manila',
  keystone_auth_host => hiera('CONFIG_CONTROLLER_HOST'),
}

class { 'manila::network::neutron':
  neutron_admin_password    => hiera('CONFIG_NEUTRON_KS_PW'),
  neutron_admin_tenant_name => 'services',
}

class { 'manila::scheduler':
}

class { 'manila::share':
}

class { 'manila::backends':
  enabled_share_backends => hiera('CONFIG_MANILA_BACKEND'),
}
