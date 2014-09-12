
remote_database { 'heat':
    ensure      => 'present',
    charset     => 'utf8',
    db_host     => '%(CONFIG_MARIADB_HOST)s',
    db_user     => '%(CONFIG_MARIADB_USER)s',
    db_password => '%(CONFIG_MARIADB_PW)s',
    provider    => 'mysql',
}

remote_database_user { 'heat@%%':
    password_hash => mysql_password('%(CONFIG_HEAT_DB_PW)s'),
    db_host       => '%(CONFIG_MARIADB_HOST)s',
    db_user       => '%(CONFIG_MARIADB_USER)s',
    db_password   => '%(CONFIG_MARIADB_PW)s',
    provider      => 'mysql',
    require       => Remote_database['heat'],
}

remote_database_grant { 'heat@%%/heat':
    privileges  => "all",
    db_host     => '%(CONFIG_MARIADB_HOST)s',
    db_user     => '%(CONFIG_MARIADB_USER)s',
    db_password => '%(CONFIG_MARIADB_PW)s',
    provider    => 'mysql',
    require     => Remote_database_user['heat@%%'],
}
