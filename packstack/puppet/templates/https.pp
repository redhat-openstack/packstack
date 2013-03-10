
class {'apache::mod::ssl': }
file {'/etc/httpd/conf.d/ssl.conf':}

file {'/etc/pki/tls/certs/ps_generate_ssl_certs.ssh':
    content => template('packstack/ssl/generate_ssl_certs.sh.erb'),
    ensure => present,
    mode => '755',
}

exec {'/etc/pki/tls/certs/ps_generate_ssl_certs.ssh':
    require => File['/etc/pki/tls/certs/ps_generate_ssl_certs.ssh'],
    notify  => Service['httpd'],
}

# close port 80
file_line{'nohttp':
    path => '/etc/httpd/conf/httpd.conf',
    match => '^#?Listen 80',
    line => '#Listen 80',
    require =>  Class['apache::mod::ssl']
}

# set the name of the ssl cert and key file
file_line{'sslcert':
    path => '/etc/httpd/conf.d/ssl.conf',
    match => '^SSLCertificateFile ',
    line => 'SSLCertificateFile /etc/pki/tls/certs/ssl_ps_server.crt',
    require =>  Class['apache::mod::ssl']
}

file_line{'sslkey':
    path => '/etc/httpd/conf.d/ssl.conf',
    match => '^SSLCertificateKeyFile ',
    line => 'SSLCertificateKeyFile /etc/pki/tls/private/ssl_ps_server.key',
    require =>  Class['apache::mod::ssl']
}
