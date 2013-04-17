class {"glance::db::mysql":
    password      => "%(CONFIG_GLANCE_DB_PW)s",
    allowed_hosts => "%%",
}
