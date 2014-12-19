
remote_database { 'ironic':
  ensure      => 'present',
  charset     => 'utf8',
  db_host     => hiera('CONFIG_MARIADB_HOST'),
  db_user     => hiera('CONFIG_MARIADB_USER'),
  db_password => hiera('CONFIG_MARIADB_PW'),
  provider    => 'mysql',
}

$mariadb_ironic_noinstall_db_pw = hiera('CONFIG_IRONIC_DB_PW')

remote_database_user { 'ironic@%%':
  password_hash => mysql_password($mariadb_ironic_noinstall_db_pw),
  db_host       => hiera('CONFIG_MARIADB_HOST'),
  db_user       => hiera('CONFIG_MARIADB_USER'),
  db_password   => hiera('CONFIG_MARIADB_PW'),
  provider      => 'mysql',
  require       => Remote_database['ironic'],
}

remote_database_grant { 'ironic@%%/ironic':
  privileges  => 'all',
  db_host     => hiera('CONFIG_MARIADB_HOST'),
  db_user     => hiera('CONFIG_MARIADB_USER'),
  db_password => hiera('CONFIG_MARIADB_PW'),
  provider    => 'mysql',
  require     => Remote_database_user['ironic@%%'],
}
