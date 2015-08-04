
require 'keystone::python'
$bind_host = hiera('CONFIG_IP_VERSION') ? {
  'ipv6' => '::0',
  'ipv4' => '0.0.0.0',
}

class { '::nova::api':
  api_bind_address                     => $bind_host,
  metadata_listen                      => $bind_host,
  enabled                              => true,
  auth_uri                             => hiera('CONFIG_KEYSTONE_PUBLIC_URL'),
  identity_uri                         => hiera('CONFIG_KEYSTONE_ADMIN_URL'),
  admin_password                       => hiera('CONFIG_NOVA_KS_PW'),
  neutron_metadata_proxy_shared_secret => hiera('CONFIG_NEUTRON_METADATA_PW_UNQUOTED', undef),
}

Package<| title == 'nova-common' |> -> Class['nova::api']

$db_purge = hiera('CONFIG_NOVA_DB_PURGE_ENABLE')
if $db_purge {
  class { '::nova::cron::archive_deleted_rows':
    hour        => '*/12',
    destination => '/dev/null',
  }
}
