class {"nova::db::mysql":
  password      => "%(CONFIG_NOVA_DB_PW)s",
  host          => "%%",
  allowed_hosts => "%%",
  charset       => "utf8",
}
