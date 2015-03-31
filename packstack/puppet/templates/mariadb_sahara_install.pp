class { '::sahara::db::mysql':
  password      => hiera('CONFIG_SAHARA_DB_PW'),
  host          => '%%',
  allowed_hosts => '%%',
}
