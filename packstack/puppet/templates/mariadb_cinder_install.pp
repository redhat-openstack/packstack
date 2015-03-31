class { '::cinder::db::mysql':
  password      => hiera('CONFIG_CINDER_DB_PW'),
  host          => '%%',
  allowed_hosts => '%%',
  charset       => 'utf8',
}
