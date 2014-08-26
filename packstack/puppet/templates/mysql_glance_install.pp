class {"glance::db::mysql":
  password      => "%(CONFIG_GLANCE_DB_PW)s",
  host          => "%%",
  allowed_hosts => "%%",
  charset       => "utf8",
  mysql_module  => '2.2',
}
