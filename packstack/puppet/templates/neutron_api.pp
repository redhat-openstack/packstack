
class { '::neutron::server':
  database_connection => $neutron_sql_connection,
  auth_password       => $neutron_user_password,
  auth_uri            => hiera('CONFIG_KEYSTONE_PUBLIC_URL'),
  identity_uri        => hiera('CONFIG_KEYSTONE_ADMIN_URL'),
  sync_db             => true,
  enabled             => true,
}

file { '/etc/neutron/api-paste.ini':
  ensure  => file,
  mode    => '0640',
}

Class['::neutron::server'] -> File['/etc/neutron/api-paste.ini']

