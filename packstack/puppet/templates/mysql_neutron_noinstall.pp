
remote_database { '%(CONFIG_NEUTRON_L2_DBNAME)s':
    ensure      => 'present',
    charset     => 'latin1',
    db_host     => '%(CONFIG_MYSQL_HOST)s',
    db_user     => '%(CONFIG_MYSQL_USER)s',
    db_password => '%(CONFIG_MYSQL_PW)s',
    provider    => 'mysql',
}

remote_database_user { 'neutron@%%':
    password_hash => mysql_password('%(CONFIG_NEUTRON_DB_PW)s' ),
    db_host       => '%(CONFIG_MYSQL_HOST)s',
    db_user       => '%(CONFIG_MYSQL_USER)s',
    db_password   => '%(CONFIG_MYSQL_PW)s',
    provider      => 'mysql',
    require       => Remote_database['%(CONFIG_NEUTRON_L2_DBNAME)s'],
}

remote_database_grant { 'neutron@%%/%(CONFIG_NEUTRON_L2_DBNAME)s':
    privileges  => "all",
    db_host     => '%(CONFIG_MYSQL_HOST)s',
    db_user     => '%(CONFIG_MYSQL_USER)s',
    db_password => '%(CONFIG_MYSQL_PW)s',
    provider    => 'mysql',
    require     => Remote_database_user['neutron@%%'],
}
