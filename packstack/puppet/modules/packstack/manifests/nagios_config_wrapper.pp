define packstack_nagios_host {
  nagios_host { $name:
    use     => 'linux-server',
    address => $name,
    owner   => 'nagios',
    group   => 'nagios',
    mode    => '0644',
  }
}

define packstack_nagios_generic_services {
  nagios_service { "load5-${name}":
    check_command         => 'check_nrpe!load5',
    host_name             => $name,
    normal_check_interval => '5',
    service_description   => '5 minute load average',
    use                   => 'generic-service',
    owner                 => 'nagios',
    group                 => 'nagios',
    mode                  => '0644',
  }
  nagios_service { "df_var${name}":
    check_command         => 'check_nrpe!df_var',
    host_name             => $name,
    service_description   => 'Percent disk space used on /var',
    use                   => 'generic-service',
    owner                 => 'nagios',
    group                 => 'nagios',
    mode                  => '0644',
  }
}

define packstack_nagios_services {
  file { "/usr/lib64/nagios/plugins/${name}":
    mode    => '0755',
    owner   => 'nagios',
    seltype => 'nagios_unconfined_plugin_exec_t',
    content => template("packstack/${name}.erb"),
  }

  nagios_command { $name:
    command_line => "/usr/lib64/nagios/plugins/${name}",
    owner        => 'nagios',
    group        => 'nagios',
    mode         => '0644',
  }

  nagios_service { $name:
    host_name             => $packstack::nagios_config_wrapper::controller_host,
    normal_check_interval => '5',
    check_command         => $name,
    use                   => 'generic-service',
    service_description   => "$name service",
    owner                 => 'nagios',
    group                 => 'nagios',
    mode                  => '0644',
 }

}

class packstack::nagios_config_wrapper (
  $nagios_hosts = [],
  $nagios_openstack_services = [],
  $controller_host,
) {
  nagios_command { 'check_nrpe':
    command_line => '/usr/lib64/nagios/plugins/check_nrpe -H $HOSTADDRESS$ -c $ARG1$',
    owner        => 'nagios',
    group        => 'nagios',
    mode         => '0644',
  }

  packstack_nagios_host { $nagios_hosts: }
  packstack_nagios_generic_services { $nagios_hosts: }
  packstack_nagios_services { $nagios_openstack_services: }
}
