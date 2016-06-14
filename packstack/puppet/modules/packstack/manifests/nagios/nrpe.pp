class packstack::nagios::nrpe ()
{
    create_resources(packstack::firewall, hiera('FIREWALL_NAGIOS_NRPE_RULES', {}))
    $nagios_configs_cfg_ctrl_host = hiera('CONFIG_CONTROLLER_HOST')
    package{ 'nrpe':
      ensure => present,
    } ->
    file{ '/etc/nagios/nrpe.cfg':
      ensure  => file,
      mode    => '0644',
      owner   => 'nagios',
      group   => 'nagios',
      require => Package['nrpe'],
    } ->
    file_line{'allowed_hosts':
      path  => '/etc/nagios/nrpe.cfg',
      match => 'allowed_hosts=',
      line  => "allowed_hosts=${nagios_configs_cfg_ctrl_host}",
    } ->

    # 5 minute load average
    file_line{'load5':
      path  => '/etc/nagios/nrpe.cfg',
      match => 'command\[load5\]=',
      line  => 'command[load5]=cut /proc/loadavg -f 1 -d " "',
    } ->

    # disk used on /var
    file_line{'df_var':
      path  => '/etc/nagios/nrpe.cfg',
      match => "command\[df_var\]=",
      line  => "command[df_var]=df /var/ | sed -re 's/.* ([0-9]+)%.*/\\1/' | grep -E '^[0-9]'",
    } ->

    service{'nrpe':
      ensure    => running,
      enable    => true,
      hasstatus => true,
    }
}
