package{['nagios', 'nagios-plugins-nrpe', 'nagios-plugins-ping']:
    ensure => present,
    before => Class['nagios_configs']
}

class nagios_configs(){
    file{['/etc/nagios/nagios_command.cfg', '/etc/nagios/nagios_host.cfg']:
        ensure => 'present',
        mode => '0644',
        owner => 'nagios',
        group => 'nagios',
    }

    # Remove the entry for localhost, it contains services we're not
    # monitoring
    file{['/etc/nagios/objects/localhost.cfg']:
        ensure => 'present',
        content => '',
    }

    file_line{'nagios_host':
        path => '/etc/nagios/nagios.cfg',
        line => 'cfg_file=/etc/nagios/nagios_host.cfg',
    }

    file_line{'nagios_command':
        path => '/etc/nagios/nagios.cfg',
        line => 'cfg_file=/etc/nagios/nagios_command.cfg',
    }

    file_line{'nagios_service':
        path => '/etc/nagios/nagios.cfg',
        line => 'cfg_file=/etc/nagios/nagios_service.cfg',
    }

    nagios_command{'check_nrpe':
        command_line => '/usr/lib64/nagios/plugins/check_nrpe -H $HOSTADDRESS$ -c $ARG1$',
    }

    exec{'nagiospasswd':
        command => '/usr/bin/htpasswd -b /etc/nagios/passwd nagiosadmin %(CONFIG_NAGIOS_PW)s',
    }

    file {"/etc/nagios/keystonerc_admin":
        ensure  => "present", owner  => "nagios", mode => '0600',
        content => "export OS_USERNAME=admin
export OS_TENANT_NAME=admin
export OS_PASSWORD=%(CONFIG_KEYSTONE_ADMIN_PW)s
export OS_AUTH_URL=http://%(CONFIG_KEYSTONE_HOST)s:35357/v2.0/ ",}

    %(CONFIG_NAGIOS_MANIFEST_CONFIG)s
}

class{'nagios_configs':
    notify => [Service['nagios'], Service['httpd']],
}

class {'apache': }
class {'apache::mod::php': }
class {'apache::mod::wsgi':}
# The apache module purges files it doesn't know about
# avoid this be referencing them here
file { '/etc/httpd/conf.d/openstack-dashboard.conf':}
file { '/etc/httpd/conf.d/rootredirect.conf':}
file { '/etc/httpd/conf.d/nagios.conf':}

service{['nagios']:
    ensure => running,
    hasstatus => true,
}

firewall { '001 nagios incoming':
    proto    => 'tcp',
    dport    => ['80'],
    action   => 'accept',
}
