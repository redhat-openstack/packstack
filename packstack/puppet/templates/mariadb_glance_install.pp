class { 'glance::db::mysql':
  password      => hiera('CONFIG_GLANCE_DB_PW'),
  host          => '%%',
  allowed_hosts => '%%',
  charset       => 'utf8',
  mysql_module  => '2.2',
}
