
remote_database { 'heat':
    ensure      => 'present',
    charset     => 'latin1',
    db_host     => '%(CONFIG_MYSQL_HOST)s',
    db_user     => '%(CONFIG_MYSQL_USER)s',
    db_password => '%(CONFIG_MYSQL_PW)s',
    provider    => 'mysql',
}

remote_database_user { 'heat@%%':
    password_hash => mysql_password('%(CONFIG_HEAT_DB_PW)s'),
    db_host       => '%(CONFIG_MYSQL_HOST)s',
    db_user       => '%(CONFIG_MYSQL_USER)s',
    db_password   => '%(CONFIG_MYSQL_PW)s',
    provider      => 'mysql',
    require       => Remote_database['heat'],
}

remote_database_grant { 'heat@%%/heat':
    privileges  => "all",
    db_host     => '%(CONFIG_MYSQL_HOST)s',
    db_user     => '%(CONFIG_MYSQL_USER)s',
    db_password => '%(CONFIG_MYSQL_PW)s',
    provider    => 'mysql',
    require     => Remote_database_user['heat@%%'],
}
