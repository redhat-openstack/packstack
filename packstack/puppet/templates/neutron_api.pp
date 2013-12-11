class { 'neutron::server':
  sql_connection => $neutron_sql_connection,
  connection => $neutron_sql_connection,
  auth_password => $neutron_user_password,
  auth_host => '%(CONFIG_KEYSTONE_HOST)s',
  enabled => true,
}

exec { 'neutron-db-manage upgrade':
  command     => 'neutron-db-manage --config-file /etc/neutron/neutron.conf --config-file /etc/neutron/plugin.ini upgrade head',
  path        => '/usr/bin',
  user        => 'neutron',
  logoutput   => 'on_failure',
  before      => Service['neutron-server'],
  require     => [Neutron_config['database/connection'], Neutron_config['DEFAULT/core_plugin']],
}
