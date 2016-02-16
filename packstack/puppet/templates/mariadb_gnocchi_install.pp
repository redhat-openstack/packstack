class { '::gnocchi::db::mysql':
  password      => hiera('CONFIG_GNOCCHI_DB_PW'),
  host          => '%%',
  allowed_hosts => '%%',
}
