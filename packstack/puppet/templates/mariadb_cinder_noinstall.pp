
remote_database { 'cinder':
    ensure      => 'present',
    charset     => 'utf8',
    db_host     => '%(CONFIG_MARIADB_HOST)s',
    db_user     => '%(CONFIG_MARIADB_USER)s',
    db_password => '%(CONFIG_MARIADB_PW)s',
    provider    => 'mysql',
}

remote_database_user { 'cinder@%%':
    password_hash => mysql_password('%(CONFIG_CINDER_DB_PW)s'),
    db_host       => '%(CONFIG_MARIADB_HOST)s',
    db_user       => '%(CONFIG_MARIADB_USER)s',
    db_password   => '%(CONFIG_MARIADB_PW)s',
    provider      => 'mysql',
    require       => Remote_database['cinder'],
}

remote_database_grant { 'cinder@%%/cinder':
    privileges  => "all",
    db_host     => '%(CONFIG_MARIADB_HOST)s',
    db_user     => '%(CONFIG_MARIADB_USER)s',
    db_password => '%(CONFIG_MARIADB_PW)s',
    provider    => 'mysql',
    require     => Remote_database_user['cinder@%%'],
}
