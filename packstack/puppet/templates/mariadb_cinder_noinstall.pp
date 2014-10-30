
remote_database { 'cinder':
  ensure      => 'present',
  charset     => 'utf8',
  db_host     => hiera('CONFIG_MARIADB_HOST'),
  db_user     => hiera('CONFIG_MARIADB_USER'),
  db_password => hiera('CONFIG_MARIADB_PW'),
  provider    => 'mysql',
}

$mariadb_cinder_noinstall_db_pw = hiera('CONFIG_CINDER_DB_PW')

remote_database_user { 'cinder@%%':
  password_hash => mysql_password($mariadb_cinder_noinstall_db_pw),
  db_host       => hiera('CONFIG_MARIADB_HOST'),
  db_user       => hiera('CONFIG_MARIADB_USER'),
  db_password   => hiera('CONFIG_MARIADB_PW'),
  provider      => 'mysql',
  require       => Remote_database['cinder'],
}

remote_database_grant { 'cinder@%%/cinder':
  privileges  => 'all',
  db_host     => hiera('CONFIG_MARIADB_HOST'),
  db_user     => hiera('CONFIG_MARIADB_USER'),
  db_password => hiera('CONFIG_MARIADB_PW'),
  provider    => 'mysql',
  require     => Remote_database_user['cinder@%%'],
}
