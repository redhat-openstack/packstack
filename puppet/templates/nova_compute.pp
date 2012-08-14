
nova_config{
    #"flat_interface": value => "eth0";
    "network_host": value => "%(CONFIG_NOVANETWORK_HOST)s";
    "libvirt_inject_partition": value => "-1";
}

class {"nova::compute":
    enabled => true,
}

class { 'nova::compute::libvirt':
  libvirt_type                => "%(CONFIG_LIBVIRT_TYPE)s",
}

if "%(CONFIG_LIBVIRT_TYPE)s" == "qemu" {
    file { "/usr/bin/qemu-system-x86_64":
        ensure => link,
        target => "/usr/libexec/qemu-kvm",
    } 
}

