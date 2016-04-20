
require 'keystone::python'
$bind_host = hiera('CONFIG_IP_VERSION') ? {
  'ipv6'  => '::0',
  default => '0.0.0.0',
  # TO-DO(mmagr): Add IPv6 support when hostnames are used
}

$config_use_neutron = hiera('CONFIG_NEUTRON_INSTALL')
if $config_use_neutron == 'y' {
    $default_floating_pool = 'public'
} else {
    $default_floating_pool = 'nova'
}

$auth_uri = hiera('CONFIG_KEYSTONE_PUBLIC_URL')
$admin_password = hiera('CONFIG_NOVA_KS_PW')

class { '::nova::api':
  api_bind_address                     => $bind_host,
  metadata_listen                      => $bind_host,
  enabled                              => true,
  auth_uri                             => $auth_uri,
  identity_uri                         => hiera('CONFIG_KEYSTONE_ADMIN_URL'),
  admin_password                       => $admin_password,
  neutron_metadata_proxy_shared_secret => hiera('CONFIG_NEUTRON_METADATA_PW_UNQUOTED', undef),
  default_floating_pool                => $default_floating_pool,
  pci_alias                            => hiera('CONFIG_NOVA_PCI_ALIAS'),
  sync_db_api                          => true,
  osapi_compute_workers                => $service_workers,
  metadata_workers                     => $service_workers
}

Package<| title == 'nova-common' |> -> Class['nova::api']

$db_purge = hiera('CONFIG_NOVA_DB_PURGE_ENABLE')
if $db_purge {
  class { '::nova::cron::archive_deleted_rows':
    hour        => '*/12',
    destination => '/dev/null',
  }
}

# TODO: Refactor flavor provisioning when https://review.openstack.org/#/c/305463/ lands
$manage_flavors = str2bool(hiera('CONFIG_NOVA_MANAGE_FLAVORS'))

if $manage_flavors {
  $os_auth_options = "--os-username nova --os-password ${admin_password} --os-tenant-name services --os-auth-url ${auth_uri}"
  Exec {
    path => '/usr/bin:/bin:/usr/sbin:/sbin'
  }

  # Manage a default set of flavors
  exec { 'manage_m1.tiny_nova_flavor':
    provider => shell,
    command  => "openstack ${os_auth_options} flavor create --id 1 --ram 512 --disk 1 --vcpus 1 m1.tiny",
    unless   => "openstack ${os_auth_options} flavor list | grep m1.tiny",
    require  => Class['::nova::api'],
  }
  exec { 'manage_m1.small_nova_flavor':
    provider => shell,
    command  => "openstack ${os_auth_options} flavor create --id 2 --ram 2048 --disk 20 --vcpus 1 m1.small",
    unless   => "openstack ${os_auth_options} flavor list | grep m1.small",
    require  => Class['::nova::api'],
  }
  exec { 'manage_m1.medium_nova_flavor':
    provider => shell,
    command  => "openstack ${os_auth_options} flavor create --id 3 --ram 4096 --disk 40 --vcpus 2 m1.medium",
    unless   => "openstack ${os_auth_options} flavor list | grep m1.medium",
    require  => Class['::nova::api'],
  }
  exec { 'manage_m1.large_nova_flavor':
    provider => shell,
    command  => "openstack ${os_auth_options} flavor create --id 4 --ram 8192 --disk 80 --vcpus 4 m1.large",
    unless   => "openstack ${os_auth_options} flavor list | grep m1.large",
    require  => Class['::nova::api'],
  }
  exec { 'manage_m1.xlarge_nova_flavor':
    provider => shell,
    command  => "openstack ${os_auth_options} flavor create --id 5 --ram 16384 --disk 160 --vcpus 8 m1.xlarge",
    unless   => "openstack ${os_auth_options} flavor list | grep m1.xlarge",
    require  => Class['::nova::api'],
  }
}
