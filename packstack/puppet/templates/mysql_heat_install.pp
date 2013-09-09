class {"heat::db::mysql":
    password      => "%(CONFIG_HEAT_DB_PW)s",
    allowed_hosts => "%%",
}
