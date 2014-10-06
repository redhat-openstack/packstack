
require 'keystone::python'
class { 'nova::api':
  enabled                              => true,
  auth_host                            => hiera('CONFIG_CONTROLLER_HOST'),
  admin_password                       => hiera('CONFIG_NOVA_KS_PW'),
  neutron_metadata_proxy_shared_secret => hiera('CONFIG_NEUTRON_METADATA_PW_UNQUOTED'),
}

Package<| title == 'nova-common' |> -> Class['nova::api']

