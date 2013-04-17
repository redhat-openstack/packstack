class {"keystone::db::mysql":
    password      => "%(CONFIG_KEYSTONE_DB_PW)s",
    allowed_hosts => "%%",
}
