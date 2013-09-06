
class {"qpid::server":
    auth => "no",
    clustered => false,
    ssl_certdb_pw      => '%(CONFIG_QPID_NSS_CERTDB_PW)s',
    ssl_cert_name      => '%(CONFIG_QPID_NSS_CERT_NAME)s',
    ssl_port           => '%(CONFIG_QPID_SSL_PORT)s',
    ssl                => %(CONFIG_QPID_ENABLE_SSL)s,
    ssl_cert          => '%(CONFIG_QPID_SSL_CERT_FILE)s',
    ssl_key           => '%(CONFIG_QPID_SSL_KEY_FILE)s'
}
   
firewall { '001 qpid incoming':
    proto    => 'tcp',
    dport    => ['5672'],
    action   => 'accept',
}
