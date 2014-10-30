include packstack::apache_common

package { ['nagios', 'nagios-plugins-nrpe']:
  ensure => present,
  before => Class['nagios_configs'],
}

# We need to preferably install nagios-plugins-ping
exec { 'nagios-plugins-ping':
  path    => '/usr/bin',
  command => 'yum install -y -d 0 -e 0 monitoring-plugins-ping',
  onlyif  => 'yum install -y -d 0 -e 0 nagios-plugins-ping &> /dev/null && exit 1 || exit 0',
  before  => Class['nagios_configs']
}

class nagios_configs(){
  file { ['/etc/nagios/nagios_command.cfg', '/etc/nagios/nagios_host.cfg']:
    ensure => 'present',
    mode   => '0644',
    owner  => 'nagios',
    group  => 'nagios',
  }

  # Remove the entry for localhost, it contains services we're not
  # monitoring
  file { ['/etc/nagios/objects/localhost.cfg']:
    ensure  => 'present',
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

  nagios_command { 'check_nrpe':
    command_line => '/usr/lib64/nagios/plugins/check_nrpe -H $HOSTADDRESS$ -c $ARG1$',
  }

  $cfg_nagios_pw = hiera('CONFIG_NAGIOS_PW')

  exec { 'nagiospasswd':
    command => "/usr/bin/htpasswd -b /etc/nagios/passwd nagiosadmin ${cfg_nagios_pw}",
  }

  $nagios_cfg_ks_adm_pw = hiera('CONFIG_KEYSTONE_ADMIN_PW')
  $nagios_cfg_ctrl_host = hiera('CONFIG_CONTROLLER_HOST')

  file { '/etc/nagios/keystonerc_admin':
      ensure  => 'present',
      owner   => 'nagios',
      mode    => '0600',
      content => "export OS_USERNAME=admin
export OS_TENANT_NAME=admin
export OS_PASSWORD=${nagios_cfg_ks_adm_pw}
export OS_AUTH_URL=http://${nagios_cfg_ctrl_host}:35357/v2.0/ ",
  }

  %(CONFIG_NAGIOS_MANIFEST_CONFIG)s
}

class { 'nagios_configs':
  notify => [Service['nagios'], Service['httpd']],
}

include concat::setup

class { 'apache':
  purge_configs => false,
}

class { 'apache::mod::php': }

service { ['nagios']:
  ensure    => running,
  enable    => true,
  hasstatus => true,
}

firewall { '001 nagios incoming':
  proto    => 'tcp',
  dport    => ['80'],
  action   => 'accept',
}

# ensure that we won't stop listening on 443 if horizon has ssl enabled
if hiera('CONFIG_HORIZON_SSL') {
  apache::listen { '443': }
}
