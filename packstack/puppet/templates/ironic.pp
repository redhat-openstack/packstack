ironic_config {
  'glance/glance_host': value => hiera('CONFIG_STORAGE_HOST');
}

class { 'ironic::api':
  auth_host      => hiera('CONFIG_CONTROLLER_HOST'),
  admin_password => hiera('CONFIG_IRONIC_KS_PW'),
}

class { 'ironic::client': }

class { 'ironic::conductor': }
