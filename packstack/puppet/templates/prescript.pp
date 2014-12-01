include firewall
# This does the initial apache setup for all components that
# require apache/httpd.
# Other packstack components that use apache should do
#   include packstack_apache_common
include ::apache

# We don't have openstack-selinux package for Fedora
if $::operatingsystem != 'Fedora' {
  package{ 'openstack-selinux':
    ensure => present,
  }
}

package { 'audit':
  ensure => present,
} ->
service { 'auditd':
  ensure => running,
  enable => true,
}

