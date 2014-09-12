
remote_database { 'nova':
    ensure      => 'present',
    charset     => 'utf8',
    db_host     => '%(CONFIG_MARIADB_HOST)s',
    db_user     => '%(CONFIG_MARIADB_USER)s',
    db_password => '%(CONFIG_MARIADB_PW)s',
    provider    => 'mysql',
}

remote_database_user { 'nova@%%':
    password_hash => mysql_password('%(CONFIG_NOVA_DB_PW)s' ),
    db_host       => '%(CONFIG_MARIADB_HOST)s',
    db_user       => '%(CONFIG_MARIADB_USER)s',
    db_password   => '%(CONFIG_MARIADB_PW)s',
    provider      => 'mysql',
    require       => Remote_database['nova'],
}

remote_database_grant { 'nova@%%/nova':
    privileges  => "all",
    db_host     => '%(CONFIG_MARIADB_HOST)s',
    db_user     => '%(CONFIG_MARIADB_USER)s',
    db_password => '%(CONFIG_MARIADB_PW)s',
    provider    => 'mysql',
    require     => Remote_database_user['nova@%%'],
}
