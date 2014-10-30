
remote_database { 'glance':
  ensure      => 'present',
  charset     => 'utf8',
  db_host     => hiera('CONFIG_MARIADB_HOST'),
  db_user     => hiera('CONFIG_MARIADB_USER'),
  db_password => hiera('CONFIG_MARIADB_PW'),
  provider    => 'mysql',
}

$mariadb_glance_noinstall_db_pw = hiera('CONFIG_GLANCE_DB_PW')

remote_database_user { 'glance@%%':
  password_hash => mysql_password($mariadb_glance_noinstall_db_pw),
  db_host       => hiera('CONFIG_MARIADB_HOST'),
  db_user       => hiera('CONFIG_MARIADB_USER'),
  db_password   => hiera('CONFIG_MARIADB_PW'),
  provider      => 'mysql',
  require       => Remote_database['glance'],
}

remote_database_grant { 'glance@%%/glance':
  privileges  => 'all',
  db_host     => hiera('CONFIG_MARIADB_HOST'),
  db_user     => hiera('CONFIG_MARIADB_USER'),
  db_password => hiera('CONFIG_MARIADB_PW'),
  provider    => 'mysql',
  require     => Remote_database_user['glance@%%'],
}
