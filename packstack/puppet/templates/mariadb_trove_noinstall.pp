
remote_database { 'trove':
  ensure      => 'present',
  charset     => 'utf8',
  db_host     => hiera('CONFIG_MARIADB_HOST'),
  db_user     => hiera('CONFIG_MARIADB_USER'),
  db_password => hiera('CONFIG_MARIADB_PW'),
  provider    => 'mysql',
}

$trove_cfg_trove_db_pw = hiera('CONFIG_TROVE_DB_PW')

remote_database_user { 'trove@%%':
  password_hash => mysql_password($trove_cfg_trove_db_pw),
  db_host       => hiera('CONFIG_MARIADB_HOST'),
  db_user       => hiera('CONFIG_MARIADB_USER'),
  db_password   => hiera('CONFIG_MARIADB_PW'),
  provider      => 'mysql',
  require       => Remote_database['trove'],
}

remote_database_grant { 'trove@%%/trove':
  privileges  => 'all',
  db_host     => hiera('CONFIG_MARIADB_HOST'),
  db_user     => hiera('CONFIG_MARIADB_USER'),
  db_password => hiera('CONFIG_MARIADB_PW'),
  provider    => 'mysql',
  require     => Remote_database_user['trove@%%'],
}
