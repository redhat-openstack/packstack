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

# This is a Hack to remove the nagios config file before each run
# to work around a puppet bug http://projects.puppetlabs.com/issues/11921
# and prevent duplicate entries
exec{'rm-nagios-files':
    path    => ['/bin', '/usr/bin'],
    command => ['rm -rf /etc/nagios/resource.d/nagios_command.cfg /etc/nagios/resource.d/nagios_host.cfg'],
    before  => Class['nagios_configs']
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
