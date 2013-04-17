class {"nova::db::mysql":
    password      => "%(CONFIG_NOVA_DB_PW)s",
    allowed_hosts => "%%",
}
