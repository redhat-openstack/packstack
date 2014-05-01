
class {'apache::mod::ssl': }

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
    match => '^.*Listen 80',
    line => '#Listen 80',
    require =>  Class['apache::mod::ssl']
}

# close port 80 on 0.0.0.0
# this line is added by the horizon class
file_line{'nohttp_ip':
    path => '/etc/httpd/conf/httpd.conf',
    match => '^.*Listen 0.0.0.0:80',
    line => '#Listen 0.0.0.0:80',
    require =>  Class['horizon']
}

$https_port = %(CONFIG_HORIZON_PORT)s


if ($::fqdn != "" and $::fqdn !~ /localhost/) {
    $vhostname = $::fqdn
}
else {
    $vhostname = '%(CONFIG_HORIZON_HOST)s'
}


file{'/etc/httpd/conf.d/openstack-dashboard-vhost-port-80.conf':
    ensure  => present,
    content => "\n<VirtualHost *:80>\n\tServerName ${vhostname}\n\tRewriteEngine On\n\tRewriteCond %%{HTTPS} !=on\n\tRewriteRule ^/?(.*) https://%%{SERVER_NAME}/$1 [R,L]\n</VirtualHost>\n",
}

file_line{'redirect':
    path    => '/etc/httpd/conf.d/openstack-dashboard.conf',
    match   => '^RedirectMatch .*',
    line    => "RedirectMatch permanent ^/$ https://%(CONFIG_HORIZON_HOST)s:${https_port}/dashboard",
    require =>  Class['horizon']
}


# if the mod_ssl apache puppet module does not install
# this file, we ensure it haves the minimum
# requirements for SSL to work
$ssl_lines = {
    'ssl_port' => {
        path  => '/etc/httpd/conf.d/ssl.conf',
        match => 'Listen .+',
        line  => 'Listen 443',
        require =>  Class['apache::mod::ssl']
    },
    'start_vhost_ssl' => {
        path => '/etc/httpd/conf.d/ssl.conf',
        line => '<VirtualHost *:443>',
        require => File_line['ssl_port'],
     },
    'ssl_engine' => {
        path => '/etc/httpd/conf.d/ssl.conf',
        match => 'SSLEngine .+',
        line => 'SSLEngine on',
        require =>   File_line['start_vhost_ssl'],
     },
    # set the name of the ssl cert and key file
    'sslcert' => {
        path => '/etc/httpd/conf.d/ssl.conf',
        match => '^SSLCertificateFile ',
        line => 'SSLCertificateFile /etc/pki/tls/certs/ssl_ps_server.crt',
        require => File_line['ssl_engine'],
    },
    'sslkey' => {
        path => '/etc/httpd/conf.d/ssl.conf',
        match => '^SSLCertificateKeyFile ',
        line => 'SSLCertificateKeyFile /etc/pki/tls/private/ssl_ps_server.key',
        require =>  File_line['sslcert'],
    },
    'end_vhost_ssl' => {
        path => '/etc/httpd/conf.d/ssl.conf',
        line => '</VirtualHost>',
        require => File_line['sslkey'],
     },
}

create_resources(file_line, $ssl_lines)
