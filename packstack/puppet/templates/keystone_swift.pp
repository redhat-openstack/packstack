$swift_protocol = 'http'
$swift_host = hiera('CONFIG_STORAGE_HOST_URL')
$swift_port = '8080'
$swift_url = "${swift_protocol}://${swift_host}:$swift_port/v1/AUTH_%%(tenant_id)s"
$swift_v3_url = "${swift_protocol}://${swift_host}:$swift_port"

class { '::swift::keystone::auth':
  region         => hiera('CONFIG_KEYSTONE_REGION'),
  password       => hiera('CONFIG_SWIFT_KS_PW'),
  public_url      => $swift_url,
  internal_url    => $swift_url,
  admin_url       => $swift_url,
  public_url_s3   => $swift_v3_url,
  internal_url_s3 => $swift_v3_url,
  admin_url_s3    => $swift_v3_url,
}
