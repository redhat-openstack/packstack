class packstack::prereqs ()
{
    package{ 'openstack-selinux':
      ensure => present,
    }

    package { 'sos':
      ensure => present,
    }

    package { 'audit':
      ensure => present,
    }
    -> service { 'auditd':
      ensure => running,
      enable => true,
    }
}
