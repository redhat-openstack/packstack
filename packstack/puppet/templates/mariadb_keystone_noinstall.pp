
remote_database { 'keystone':
    ensure      => 'present',
    charset     => 'utf8',
    db_host     => '%(CONFIG_MARIADB_HOST)s',
    db_user     => '%(CONFIG_MARIADB_USER)s',
    db_password => '%(CONFIG_MARIADB_PW)s',
    provider    => 'mysql',
}

remote_database_user { 'keystone_admin@%%':
    password_hash => mysql_password('%(CONFIG_KEYSTONE_DB_PW)s' ),
    db_host       => '%(CONFIG_MARIADB_HOST)s',
    db_user       => '%(CONFIG_MARIADB_USER)s',
    db_password   => '%(CONFIG_MARIADB_PW)s',
    provider      => 'mysql',
    require       => Remote_database['keystone'],
}

remote_database_grant { 'keystone_admin@%%/keystone':
    privileges  => "all",
    db_host     => '%(CONFIG_MARIADB_HOST)s',
    db_user     => '%(CONFIG_MARIADB_USER)s',
    db_password => '%(CONFIG_MARIADB_PW)s',
    provider    => 'mysql',
    require     => Remote_database_user['keystone_admin@%%'],
}
