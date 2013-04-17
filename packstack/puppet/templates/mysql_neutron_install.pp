class {"neutron::db::mysql":
    password      => "%(CONFIG_NEUTRON_DB_PW)s",
    allowed_hosts => "%%",
    dbname        => '%(CONFIG_NEUTRON_L2_DBNAME)s',
}
