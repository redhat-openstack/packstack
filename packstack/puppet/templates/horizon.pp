$horizon_packages = ["python-memcached", "python-netaddr"]

include concat::setup

package {$horizon_packages:
    notify => Class["horizon"],
    ensure => present,
}

file {"/etc/httpd/conf.d/rootredirect.conf":
    ensure => present,
    content => 'RedirectMatch ^/$ /dashboard/',
    notify => File["/etc/httpd/conf.d/openstack-dashboard.conf"],
}

class {'horizon':
   secret_key => '%(CONFIG_HORIZON_SECRET_KEY)s',
   keystone_host => '%(CONFIG_KEYSTONE_HOST)s',
   fqdn => ['%(CONFIG_HORIZON_HOST)s', "$::fqdn", 'localhost'],
   can_set_mount_point => 'False',
   help_url =>'https://access.redhat.com/site/documentation//en-US/Red_Hat_Enterprise_Linux_OpenStack_Platform/4/index.html',
   django_debug => %(CONFIG_DEBUG_MODE)s ? {true => 'True', false => 'False'},
}

class {'memcached':}

$firewall_port = %(CONFIG_HORIZON_PORT)s

firewall { '001 horizon ${firewall_port}  incoming':
    proto    => 'tcp',
    dport    => [%(CONFIG_HORIZON_PORT)s],
    action   => 'accept',
}

if ($::selinux != "false"){
    selboolean{'httpd_can_network_connect':
        value => on,
        persistent => true,
    }
}
