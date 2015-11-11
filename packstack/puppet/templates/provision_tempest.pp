$provision_demo            = str2bool(hiera('CONFIG_PROVISION_DEMO'))
if $provision_demo {
  $username             = 'demo'
  $password             = hiera('CONFIG_KEYSTONE_DEMO_PW')
  $tenant_name          = 'demo'
  $floating_range       = hiera('CONFIG_PROVISION_DEMO_FLOATRANGE')
} else {
  $username             = hiera('CONFIG_PROVISION_TEMPEST_USER')
  $password             = hiera('CONFIG_PROVISION_TEMPEST_USER_PW')
  $tenant_name          = 'tempest'
  $floating_range       = hiera('CONFIG_PROVISION_TEMPEST_FLOATRANGE')
}

# Authentication/Keystone
$identity_uri          = hiera('CONFIG_KEYSTONE_PUBLIC_URL')
$identity_uri_v3       = regsubst($identity_uri, 'v2.0', 'v3')
$auth_version          = regsubst(hiera('CONFIG_KEYSTONE_API_VERSION'), '.0', '')
$admin_username        = hiera('CONFIG_KEYSTONE_ADMIN_USERNAME')
$admin_password        = hiera('CONFIG_KEYSTONE_ADMIN_PW')
$admin_tenant_name     = 'admin'
$admin_domain_name     = 'Default'

# get image and network id
$configure_images          = true
$configure_networks        = true

# Image
$image_name         = hiera('CONFIG_PROVISION_IMAGE_NAME')
$image_ssh_user     = hiera('CONFIG_PROVISION_IMAGE_SSH_USER')
$image_name_alt     = "${image_name}_alt"
$image_alt_ssh_user = hiera('CONFIG_PROVISION_IMAGE_SSH_USER')
$image_source       = hiera('CONFIG_PROVISION_IMAGE_URL')
$image_format       = hiera('CONFIG_PROVISION_IMAGE_FORMAT')

# network name
$public_network_name = 'public'

# nova should be able to resize with packstack setup
$resize_available          = true

$change_password_available = undef
$allow_tenant_isolation    = true
$log_file                  = 'tempest.log'
$use_stderr                = false
$debug                     = true
$public_router_id          = undef

# Tempest
$tempest_repo_uri      = hiera('CONFIG_PROVISION_TEMPEST_REPO_URI')
$tempest_repo_revision = hiera('CONFIG_PROVISION_TEMPEST_REPO_REVISION')
$tempest_clone_path    = '/var/lib/tempest'
$tempest_clone_owner   = 'root'
$setup_venv            = true
$tempest_user          = hiera('CONFIG_PROVISION_TEMPEST_USER')
$tempest_password      = hiera('CONFIG_PROVISION_TEMPEST_USER_PW')

# Service availability for testing based on configuration
$cinder_available     = str2bool(hiera('CONFIG_CINDER_INSTALL'))
$glance_available     = str2bool(hiera('CONFIG_GLANCE_INSTALL'))
$horizon_available    = str2bool(hiera('CONFIG_HORIZON_INSTALL'))
$nova_available       = str2bool(hiera('CONFIG_NOVA_INSTALL'))
$neutron_available    = str2bool(hiera('CONFIG_NEUTRON_INSTALL'))
$ceilometer_available = str2bool(hiera('CONFIG_CEILOMETER_INSTALL'))
$trove_available      = str2bool(hiera('CONFIG_TROVE_INSTALL'))
$sahara_available     = str2bool(hiera('CONFIG_SAHARA_INSTALL'))
$heat_available       = str2bool(hiera('CONFIG_HEAT_INSTALL'))
$swift_available      = str2bool(hiera('CONFIG_SWIFT_INSTALL'))
$configure_tempest    = str2bool(hiera('CONFIG_PROVISION_TEMPEST'))

# on standalone install we depend on this package
package {'python-openstackclient':
  before => Class['::tempest'],
}

class { '::tempest':
  admin_username            => $admin_username,
  admin_password            => $admin_password,
  admin_tenant_name         => $admin_tenant_name,
  admin_domain_name         => $admin_domain_name,
  username                  => $username,
  tenant_name               => $tenant_name,
  password                  => $password,
  identity_uri              => $identity_uri,
  identity_uri_v3           => $identity_uri_v3,
  auth_version              => $auth_version,
  configure_images          => $configure_images,
  configure_networks        => $configure_networks,
  image_name                => $image_name,
  image_ssh_user            => $image_ssh_user,
  image_name_alt            => $image_name_alt,
  image_alt_ssh_user        => $image_alt_ssh_user,
  public_network_name       => $public_network_name,
  resize_available          => $resize_available,
  change_password_available => $change_password_available,
  allow_tenant_isolation    => $allow_tenant_isolation,
  log_file                  => $log_file,
  use_stderr                => $use_stderr,
  debug                     => $debug,
  public_router_id          => $public_router_id,
  glance_available          => $glance_available,
  horizon_available         => $horizon_available,
  nova_available            => $nova_available,
  neutron_available         => $neutron_available,
  ceilometer_available      => $ceilometer_available,
  trove_available           => $trove_available,
  sahara_available          => $sahara_available,
  heat_available            => $heat_available,
  swift_available           => $swift_available,
  tempest_repo_uri          => $tempest_repo_uri,
  tempest_clone_path        => $tempest_clone_path,
  tempest_clone_owner       => $tempest_clone_owner,
  tempest_repo_revision     => $tempest_repo_revision,
  setup_venv                => $setup_venv,
}

tempest_config { 'object-storage/operator_role':
  value => 'SwiftOperator',
  path  => "${tempest_clone_path}/etc/tempest.conf",
}

