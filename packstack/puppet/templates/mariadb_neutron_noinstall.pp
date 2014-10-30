
$mariadb_neutron_noinstall_db_pw     = hiera('CONFIG_NEUTRON_DB_PW')
$mariadb_neutron_noinstall_l2_dbname = hiera('CONFIG_NEUTRON_L2_DBNAME')

remote_database { $mariadb_neutron_noinstall_l2_dbname:
  ensure      => present,
  charset     => 'utf8',
  db_host     => hiera('CONFIG_MARIADB_HOST'),
  db_user     => hiera('CONFIG_MARIADB_USER'),
  db_password => hiera('CONFIG_MARIADB_PW'),
  provider    => 'mysql',
}

remote_database_user { 'neutron@%%':
  password_hash => mysql_password($mariadb_neutron_noinstall_db_pw),
  db_host       => hiera('CONFIG_MARIADB_HOST'),
  db_user       => hiera('CONFIG_MARIADB_USER'),
  db_password   => hiera('CONFIG_MARIADB_PW'),
  provider      => 'mysql',
  require       => Remote_database[$mariadb_neutron_noinstall_l2_dbname],
}

remote_database_grant { "neutron@%%/${mariadb_neutron_noinstall_l2_dbname}":
  privileges  => 'all',
  db_host     => hiera('CONFIG_MARIADB_HOST'),
  db_user     => hiera('CONFIG_MARIADB_USER'),
  db_password => hiera('CONFIG_MARIADB_PW'),
  provider    => 'mysql',
  require     => Remote_database_user['neutron@%%'],
}
