class {"heat::db::mysql":
  password      => "%(CONFIG_HEAT_DB_PW)s",
  host          => "%%",
  allowed_hosts => "%%",
  charset       => "utf8",
  mysql_module  => '2.2',
}
