class { '::keystone::db::mysql':
  user          => 'keystone_admin',
  password      => hiera('CONFIG_KEYSTONE_DB_PW'),
  allowed_hosts => '%%',
  charset       => 'utf8',
}
