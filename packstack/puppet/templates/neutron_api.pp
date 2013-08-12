class { 'neutron::server':
  auth_password => $neutron_user_password,
  auth_host => '%(CONFIG_KEYSTONE_HOST)s',
  enabled => true,
}

firewall { '001 neutron incoming':
    proto    => 'tcp',
    dport    => ['9696'],
    action   => 'accept',
}
