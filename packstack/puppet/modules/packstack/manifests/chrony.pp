class packstack::chrony ()
{
    $cfg_ntp_server_def = lookup('CONFIG_NTP_SERVER_DEF')
    $cfg_ntp_servers    = lookup('CONFIG_NTP_SERVERS')

    $config_content = "
    # Use public servers from the pool.ntp.org project.
    # Please consider joining the pool (http://www.pool.ntp.org/join.html).
    ${cfg_ntp_server_def}

    # Ignore stratum in source selection.
    stratumweight 0

    # Record the rate at which the system clock gains/losses time.
    driftfile /var/lib/chrony/drift

    # Enable kernel RTC synchronization.
    rtcsync

    # In first three updates step the system clock instead of slew
    # if the adjustment is larger than 10 seconds.
    makestep 10 3

    # Allow NTP client access from local network.
    #allow 192.168/16

    # Listen for commands only on localhost.
    bindcmdaddress 127.0.0.1
    bindcmdaddress ::1

    # Serve time even if not synchronized to any NTP server.
    #local stratum 10

    keyfile /etc/chrony.keys

    # Specify the key used as password for chronyc.
    commandkey 1

    # Generate command key if missing.
    generatecommandkey

    # Disable logging of client accesses.
    noclientlog

    # Send a message to syslog if a clock adjustment is larger than 0.5 seconds.
    logchange 0.5

    logdir /var/log/chrony
    #log measurements statistics tracking
    "

    package { 'chrony':
      ensure => 'installed',
      name   => 'chrony',
    }

    file { 'chrony_conf':
      ensure  => file,
      path    => '/etc/chrony.conf',
      mode    => '0644',
      content => $config_content,
    }

    exec { 'stop-chronyd':
      path    => '/bin:/usr/bin:/sbin:/usr/sbin',
      command => 'systemctl stop chronyd.service',
      onlyif  => 'systemctl status chronyd.service'
    }

    exec { 'ntpdate':
      command => "/usr/bin/chronyc makestep",
      tries   => 3,
    }

    service { 'chronyd':
      ensure     => running,
      enable     => true,
      name       => 'chronyd',
      hasstatus  => true,
      hasrestart => true,
    }

    Package['chrony']
    -> File['chrony_conf']
    -> Exec['stop-chronyd']
    -> Service['chronyd']
    -> Exec['ntpdate']
}
