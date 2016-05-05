package { ['nagios', 'nagios-plugins-nrpe']:
  ensure => present,
  before => Class['nagios_configs'],
}

# We need to preferably install nagios-plugins-ping
exec { 'nagios-plugins-ping':
  path    => '/usr/bin',
  command => 'yum install -y -d 0 -e 0 monitoring-plugins-ping',
  onlyif  => 'yum install -y -d 0 -e 0 nagios-plugins-ping &> /dev/null && exit 1 || exit 0',
  before  => Class['nagios_configs'],
}

class nagios_configs(){
  file { ['/etc/nagios/nagios_command.cfg', '/etc/nagios/nagios_host.cfg', '/etc/nagios/nagios_service.cfg']:
    ensure => file,
    mode   => '0644',
    owner  => 'nagios',
    group  => 'nagios',
  }

  # Remove the entry for localhost, it contains services we're not
  # monitoring
  file { ['/etc/nagios/objects/localhost.cfg']:
    ensure  => file,
    content => '',
  }

  file_line { 'nagios_host':
    path => '/etc/nagios/nagios.cfg',
    line => 'cfg_file=/etc/nagios/nagios_host.cfg',
  }

  file_line { 'nagios_command':
    path => '/etc/nagios/nagios.cfg',
    line => 'cfg_file=/etc/nagios/nagios_command.cfg',
  }

  file_line { 'nagios_service':
    path => '/etc/nagios/nagios.cfg',
    line => 'cfg_file=/etc/nagios/nagios_service.cfg',
  }

  $nagios_cfg_ks_adm_pw = hiera('CONFIG_KEYSTONE_ADMIN_PW')
  $nagios_cfg_keystone_url = hiera('CONFIG_KEYSTONE_ADMIN_URL')
  $keystone_admin_username = hiera('CONFIG_KEYSTONE_ADMIN_USERNAME')

  file { '/etc/nagios/keystonerc_admin':
    ensure  => file,
    owner   => 'nagios',
    mode    => '0600',
    content => "export OS_USERNAME=${keystone_admin_username}
export OS_TENANT_NAME=admin
export OS_PASSWORD=${nagios_cfg_ks_adm_pw}
export OS_AUTH_URL=${nagios_cfg_keystone_url}",
  }

  class { 'packstack::nagios_config_wrapper':
    nagios_hosts              => hiera('CONFIG_NAGIOS_NODES'),
    nagios_openstack_services => hiera('CONFIG_NAGIOS_SERVICES'),
    controller_host           => hiera('CONFIG_CONTROLLER_HOST'),
    require                   => Package['nagios'],
    notify                    => Service['nagios'],
  }
}

class { '::nagios_configs':
  notify => [ Service['nagios'], Service['httpd']],
}

class { '::apache':
  purge_configs => false,
}

$cfg_nagios_pw = hiera('CONFIG_NAGIOS_PW')

exec { 'nagiospasswd':
  command => "/usr/bin/htpasswd -b /etc/nagios/passwd nagiosadmin ${cfg_nagios_pw}",
  require => Package['nagios'],
  before  => Service['nagios'],
}

class { '::apache::mod::php': }

service { ['nagios']:
  ensure    => running,
  enable    => true,
  hasstatus => true,
}

firewall { '001 nagios incoming':
  proto  => 'tcp',
  dport  => ['80'],
  action => 'accept',
}
