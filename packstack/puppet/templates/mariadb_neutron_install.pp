class { '::neutron::db::mysql':
  password      => hiera('CONFIG_NEUTRON_DB_PW'),
  host          => '%%',
  allowed_hosts => '%%',
  dbname        => hiera('CONFIG_NEUTRON_L2_DBNAME'),
  charset       => 'utf8',
}
