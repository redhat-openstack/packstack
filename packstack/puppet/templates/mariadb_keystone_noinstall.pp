
remote_database { 'keystone':
  ensure      => 'present',
  charset     => 'utf8',
  db_host     => hiera('CONFIG_MARIADB_HOST'),
  db_user     => hiera('CONFIG_MARIADB_USER'),
  db_password => hiera('CONFIG_MARIADB_PW'),
  provider    => 'mysql',
}

$mariadb_keystone_noinstall_db_pw = hiera('CONFIG_KEYSTONE_DB_PW')

remote_database_user { 'keystone_admin@%%':
  password_hash => mysql_password($mariadb_keystone_noinstall_db_pw),
  db_host       => hiera('CONFIG_MARIADB_HOST'),
  db_user       => hiera('CONFIG_MARIADB_USER'),
  db_password   => hiera('CONFIG_MARIADB_PW'),
  provider      => 'mysql',
  require       => Remote_database['keystone'],
}

remote_database_grant { 'keystone_admin@%%/keystone':
  privileges  => 'all',
  db_host     => hiera('CONFIG_MARIADB_HOST'),
  db_user     => hiera('CONFIG_MARIADB_USER'),
  db_password => hiera('CONFIG_MARIADB_PW'),
  provider    => 'mysql',
  require     => Remote_database_user['keystone_admin@%%'],
}
