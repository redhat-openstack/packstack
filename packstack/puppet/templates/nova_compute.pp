
# Ensure Firewall changes happen before libvirt service start
# preventing a clash with rules being set by libvirt
Firewall <| |> -> Class['nova::compute::libvirt']

if $::is_virtual_packstack == "true" {
    $libvirt_type = "qemu"
    nova_config{
        "DEFAULT/libvirt_cpu_mode": value => "none";
    }
}else{
    $libvirt_type = "kvm"
}

package{'python-cinderclient':
    before => Class["nova"]
}

nova_config{
    "DEFAULT/libvirt_inject_partition": value => "-1";
    "DEFAULT/volume_api_class": value => "nova.volume.cinder.API";
}

class {"nova::compute":
    enabled => true,
    vncproxy_host => "%(CONFIG_NOVA_VNCPROXY_HOST)s",
    vncserver_proxyclient_address => "%(CONFIG_NOVA_COMPUTE_HOST)s",
}

exec { 'qemu-kvm':
    path => '/usr/bin',
    command => 'yum install -y qemu-kvm',
    before => Class['nova::compute::libvirt']
}

class { 'nova::compute::libvirt':
  libvirt_type                => "$libvirt_type",
  vncserver_listen            => "%(CONFIG_NOVA_COMPUTE_HOST)s",
}

exec {'load_kvm':
    user => 'root',
    command => '/bin/sh /etc/sysconfig/modules/kvm.modules',
    onlyif => '/usr/bin/test -e /etc/sysconfig/modules/kvm.modules',
}

Class['nova::compute']-> Exec["load_kvm"]

# Note : remove this once we're installing a version of openstack that isn't
#        supported on RHEL 6.3
if $::is_virtual_packstack == "true" and $::osfamily == "RedHat" and
    $::operatingsystemrelease == "6.3"{
    file { "/usr/bin/qemu-system-x86_64":
        ensure => link,
        target => "/usr/libexec/qemu-kvm",
        notify => Service["nova-compute"],
    }
}

# Tune the host with a virtual hosts profile
package {'tuned':
    ensure => present,
}

service {'tuned':
    ensure => running,
    require => Package['tuned'],
}

if $::operatingsystem == 'Fedora' and $::operatingsystemrelease == 19 {
    # older tuned service is sometimes stucked on Fedora 19
    exec {'tuned-update':
       path => ['/sbin', '/usr/sbin', '/bin', '/usr/bin'],
       command => 'yum update -y tuned',
       logoutput => 'on_failure',
    }

    exec {'tuned-restart':
       path => ['/sbin', '/usr/sbin', '/bin', '/usr/bin'],
       command => 'systemctl restart tuned.service',
       logoutput => 'on_failure',
    }

    Service['tuned'] -> Exec['tuned-update'] -> Exec['tuned-restart'] -> Exec['tuned-virtual-host']
}

exec {'tuned-virtual-host':
    unless => '/usr/sbin/tuned-adm active | /bin/grep virtual-host',
    command => '/usr/sbin/tuned-adm profile virtual-host',
    require => Service['tuned'],
}

file_line { 'libvirt-guests':
    path  => '/etc/sysconfig/libvirt-guests',
    line  => 'ON_BOOT=ignore',
    match => '^[\s#]*ON_BOOT=.*',
    require => Class['nova::compute::libvirt']
}

# Remove libvirt's default network (usually virbr0) as it's unnecessary and can be confusing
exec {'virsh-net-destroy-default':
    onlyif  => '/usr/bin/virsh net-list | grep default',
    command => '/usr/bin/virsh net-destroy default',
    require => Package['libvirt'],
}

exec {'virsh-net-undefine-default':
    onlyif  => '/usr/bin/virsh net-list --inactive | grep default',
    command => '/usr/bin/virsh net-undefine default',
    require => Exec['virsh-net-destroy-default'],
}
