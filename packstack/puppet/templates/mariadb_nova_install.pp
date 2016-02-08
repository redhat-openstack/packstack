class { '::nova::db::mysql':
  password      => hiera('CONFIG_NOVA_DB_PW'),
  host          => '%%',
  allowed_hosts => '%%',
  charset       => 'utf8',
}
class { '::nova::db::mysql_api':
  password      => hiera('CONFIG_NOVA_DB_PW'),
  host          => '%%',
  allowed_hosts => '%%',
  charset       => 'utf8',
}