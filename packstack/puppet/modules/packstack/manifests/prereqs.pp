class packstack::prereqs ()
{
    include ::firewall

    # We don't have openstack-selinux package for Fedora
    if $::operatingsystem != 'Fedora' {
      package{ 'openstack-selinux':
        ensure => present,
      }
    }

    package { 'sos':
      ensure => present,
    }

    package { 'audit':
      ensure => present,
    } ->
    service { 'auditd':
      ensure => running,
      enable => true,
    }
}
