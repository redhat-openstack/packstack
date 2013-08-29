class {"cinder::db::mysql":
    password      => "%(CONFIG_CINDER_DB_PW)s",
    allowed_hosts => "%%",
}
