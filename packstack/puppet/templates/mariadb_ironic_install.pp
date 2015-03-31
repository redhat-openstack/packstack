class { '::ironic::db::mysql':
  password      => hiera('CONFIG_IRONIC_DB_PW'),
  host          => '%%',
  allowed_hosts => '%%',
  charset       => 'utf8',
}
