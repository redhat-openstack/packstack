class { '::heat::db::mysql':
  password      => hiera('CONFIG_HEAT_DB_PW'),
  host          => '%%',
  allowed_hosts => '%%',
  charset       => 'utf8',
}
