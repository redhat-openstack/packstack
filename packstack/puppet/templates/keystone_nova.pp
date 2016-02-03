$nova_protocol = 'http'
$nova_host = hiera('CONFIG_KEYSTONE_HOST_URL')
$nova_port = '8774'
$nova_url = "${nova_protocol}://${nova_host}:$nova_port/v2/%%(tenant_id)s"
$nova_v3_url = "${nova_protocol}://${nova_host}:$nova_port/v3"

class { '::nova::keystone::auth':
  region          => hiera('CONFIG_KEYSTONE_REGION'),
  password        => hiera('CONFIG_NOVA_KS_PW'),
  public_url      => $nova_url,
  admin_url       => $nova_url,
  internal_url    => $nova_url,
  public_url_v3   => $nova_v3_url,
  admin_url_v3    => $nova_v3_url,
  internal_url_v3 => $nova_v3_url,
}
