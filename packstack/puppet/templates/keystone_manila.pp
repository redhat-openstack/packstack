$manila_protocol = 'http'
$manila_host = hiera('CONFIG_STORAGE_HOST_URL')
$manila_port = '8786'
$manila_url = "${manila_protocol}://${manila_host}:$manila_port/v1/%%(tenant_id)s"

class { '::manila::keystone::auth':
  password     => hiera('CONFIG_MANILA_KS_PW'),
  public_url   => $manila_url,
  admin_url    => $manila_url,
  internal_url => $manila_url,
}
