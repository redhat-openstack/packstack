class { 'manila::db::mysql':
  password      => hiera('CONFIG_MANILA_DB_PW'),
  allowed_hosts => '%%',
  charset       => 'utf8',
}
