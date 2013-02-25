package{['nagios', 'nagios-plugins-nrpe', 'nagios-plugins-ping']:
    ensure => present,
    before => Class['nagios_configs']
}

file { 'resource-d':
    path   => '/etc/nagios/resource.d',
    ensure => directory,
    owner  => 'nagios',
    before => Class['nagios_configs'],
    require => Package['nagios']
}

class nagios_configs(){
    file{['/etc/nagios/resource.d/nagios_command.cfg', '/etc/nagios/resource.d/nagios_host.cfg']:
        ensure => 'present',
        mode => '0644',
    }

    # Remove the entry for localhost, it contains services we're not
    # monitoring
    file{['/etc/nagios/objects/localhost.cfg']:
        ensure => 'present',
        content => '',
    }

    Nagios_command{
        target => '/etc/nagios/resource.d/nagios_command.cfg'
    }
    Nagios_host{
        target => '/etc/nagios/resource.d/nagios_host.cfg'
    }

    file_line{'resource.d':
        path => '/etc/nagios/nagios.cfg',
        line => 'cfg_dir=/etc/nagios/resource.d',
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

service{['nagios', 'httpd']: 
    ensure => running,
    hasstatus => true,
}
