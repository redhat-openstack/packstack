class { '::trove::db::mysql':
  password      => hiera('CONFIG_TROVE_DB_PW'),
  host          => '%%',
  allowed_hosts => '%%',
  charset       => 'utf8',
}
