class {"cinder::db::mysql":
  password      => "%(CONFIG_CINDER_DB_PW)s",
  host          => "%%",
  allowed_hosts => "%%",
  charset       => "utf8",
}
