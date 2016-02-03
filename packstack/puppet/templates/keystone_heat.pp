$heat_protocol = 'http'
$heat_port = '8004'
$heat_api_host = hiera('CONFIG_KEYSTONE_HOST_URL')
$heat_url = "${heat_protocol}://${heat_api_host}:${heat_port}/v1/%%(tenant_id)s"

# heat::keystone::auth
class { '::heat::keystone::auth':
  region                    => hiera('CONFIG_KEYSTONE_REGION'),
  password                  => hiera('CONFIG_HEAT_KS_PW'),
  public_url                => $heat_url,
  admin_url                 => $heat_url,
  internal_url              => $heat_url,
  configure_delegated_roles => true,
}

$is_heat_cfn_install = hiera('CONFIG_HEAT_CFN_INSTALL')

if $is_heat_cfn_install == 'y' {
  $heat_cfn_protocol = 'http'
  $heat_cfn_port = '8000'
  $heat_cfn_api_host = hiera('CONFIG_KEYSTONE_HOST_URL')
  $heat_cfn_url = "${heat_cfn_protocol}://${heat_cfn_api_host}:${heat_cfn_port}/v1/%%(tenant_id)s"

  # heat::keystone::cfn
  class { '::heat::keystone::auth_cfn':
    password         => hiera('CONFIG_HEAT_KS_PW'),
    public_url   => $heat_cfn_url,
    admin_url    => $heat_cfn_url,
    internal_url => $heat_cfn_url,
  }
}
