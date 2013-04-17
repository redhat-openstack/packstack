
remote_database { 'keystone':
    ensure      => 'present',
    charset     => 'latin1',
    db_host     => '%(CONFIG_MYSQL_HOST)s',
    db_user     => '%(CONFIG_MYSQL_USER)s',
    db_password => '%(CONFIG_MYSQL_PW)s',
    provider    => 'mysql',
}

remote_database_user { 'keystone_admin@%%':
    password_hash => mysql_password('%(CONFIG_KEYSTONE_DB_PW)s' ),
    db_host       => '%(CONFIG_MYSQL_HOST)s',
    db_user       => '%(CONFIG_MYSQL_USER)s',
    db_password   => '%(CONFIG_MYSQL_PW)s',
    provider      => 'mysql',
    require       => Remote_database['keystone'],
}

remote_database_grant { 'keystone_admin@%%/keystone':
    privileges  => "all",
    db_host     => '%(CONFIG_MYSQL_HOST)s',
    db_user     => '%(CONFIG_MYSQL_USER)s',
    db_password => '%(CONFIG_MYSQL_PW)s',
    provider    => 'mysql',
    require     => Remote_database_user['keystone_admin@%%'],
}
