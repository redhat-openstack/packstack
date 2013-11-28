$enable_auth = '%(CONFIG_QPID_ENABLE_AUTH)s'

class {"qpid::server":
    config_file => $::operatingsystem? {
        'Fedora' => '/etc/qpid/qpidd.conf',
        default  => '/etc/qpidd.conf',
        },
    auth => $enable_auth ? {
        'y'  => 'yes',
        default => 'no',
        },
    clustered => false,
    ssl_port      => '%(CONFIG_QPID_SSL_PORT)s',
    ssl           => %(CONFIG_QPID_ENABLE_SSL)s,
    ssl_cert      => '%(CONFIG_QPID_SSL_CERT_FILE)s',
    ssl_key       => '%(CONFIG_QPID_SSL_KEY_FILE)s',
    ssl_database_password => '%(CONFIG_QPID_NSS_CERTDB_PW)s',
}
