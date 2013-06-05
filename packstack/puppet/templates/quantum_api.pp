class { 'quantum::server':
  auth_password => $quantum_user_password,
  auth_host => '%(CONFIG_KEYSTONE_HOST)s',
  enabled => true,
}

firewall { '001 quantum incoming':
    proto    => 'tcp',
    dport    => ['9696'],
    action   => 'accept',
}
