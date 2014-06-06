$horizon_packages = ["python-memcached", "python-netaddr"]

include concat::setup

package {$horizon_packages:
    notify => Class["horizon"],
    ensure => present,
}

class {'horizon':
   secret_key => '%(CONFIG_HORIZON_SECRET_KEY)s',
   keystone_host => '%(CONFIG_CONTROLLER_HOST)s',
   keystone_default_role => '_member_',
   fqdn => ['%(CONFIG_CONTROLLER_HOST)s', "$::fqdn", 'localhost'],
   can_set_mount_point => 'False',
   help_url =>'http://docs.openstack.org',
   django_debug => %(CONFIG_DEBUG_MODE)s ? {true => 'True', false => 'False'},
}

class {'memcached':}

$firewall_port = %(CONFIG_HORIZON_PORT)s

firewall { "001 horizon ${firewall_port}  incoming":
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
