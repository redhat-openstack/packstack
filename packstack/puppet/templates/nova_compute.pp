
nova_config{
    "network_host": value => "%(CONFIG_NOVA_NETWORK_HOST)s";
    "libvirt_inject_partition": value => "-1";
}

class {"nova::compute":
    enabled => true,
    vncproxy_host => "%(CONFIG_NOVA_VNCPROXY_HOST)s",
    vncserver_proxyclient_address => "%(CONFIG_NOVA_COMPUTE_HOST)s",
}

class { 'nova::compute::libvirt':
  libvirt_type                => "%(CONFIG_LIBVIRT_TYPE)s",
  vncserver_listen            => "%(CONFIG_NOVA_COMPUTE_HOST)s",
}

if "%(CONFIG_LIBVIRT_TYPE)s" == "qemu" and $::operatingsystem == "RedHat" {
    file { "/usr/bin/qemu-system-x86_64":
        ensure => link,
        target => "/usr/libexec/qemu-kvm",
        notify => Service["nova-compute"],
    }
}

firewall { '001 nove compute incoming':
    proto    => 'tcp',
    dport    => '5900-5999',
    action   => 'accept',
}
