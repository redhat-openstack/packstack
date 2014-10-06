class { 'nova::db::mysql':
  password      => hiera('CONFIG_NOVA_DB_PW'),
  host          => '%%',
  allowed_hosts => '%%',
  charset       => 'utf8',
  mysql_module  => '2.2',
}
