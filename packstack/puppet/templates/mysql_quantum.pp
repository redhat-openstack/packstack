class {"quantum::db::mysql":
    password      => "%(CONFIG_QUANTUM_DB_PW)s",
    allowed_hosts => "%%",
    dbname        => '%(CONFIG_QUANTUM_L2_DBNAME)s',
}
