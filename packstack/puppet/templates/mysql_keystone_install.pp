class {"keystone::db::mysql":
    user          => 'keystone_admin',
    password      => "%(CONFIG_KEYSTONE_DB_PW)s",
    allowed_hosts => "%%",
    charset       => "utf8",
    mysql_module  => '2.2',
}
