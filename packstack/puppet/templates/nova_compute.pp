

if $::is_virtual_packstack == "true" {
    $libvirt_type = "qemu"
    nova_config{
        "libvirt_cpu_mode": value => "none";
    }
}else{
    $libvirt_type = "kvm"
}

package{'python-cinderclient':
    before => Class["nova"]
}

nova_config{
    "network_host": value => "%(CONFIG_NOVA_NETWORK_HOST)s";
    "libvirt_inject_partition": value => "-1";
    "volume_api_class": value => "nova.volume.cinder.API";
}

class {"nova::compute":
    enabled => true,
    vncproxy_host => "%(CONFIG_NOVA_VNCPROXY_HOST)s",
    vncserver_proxyclient_address => "%(CONFIG_NOVA_COMPUTE_HOST)s",
}

class { 'nova::compute::libvirt':
  libvirt_type                => "$libvirt_type",
  vncserver_listen            => "%(CONFIG_NOVA_COMPUTE_HOST)s",
}

exec {'load_kvm':
    user => 'root',
    command => '/bin/sh /etc/sysconfig/modules/kvm.modules'
}

Class['nova::compute']-> Exec["load_kvm"]

if $::is_virtual_packstack == "true" and $::operatingsystem == "RedHat" {
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


# Tune the host with a virtual hosts profile
package {'tuned':
    ensure => present,
}

service {'tuned':
    ensure => running,
    require => Package['tuned'],
}

exec {'tuned-virtual-host':
    unless => '/usr/sbin/tuned-adm active | /bin/grep virtual-host',
    command => '/usr/sbin/tuned-adm profile virtual-host',
    require => Service['tuned'],
}
