
class { 'heat::api_cfn':
}

class { 'heat::keystone::auth_cfn':
  admin_address      => '%(CONFIG_CONTROLLER_HOST)s',
  public_address     => '%(CONFIG_CONTROLLER_HOST)s',
  internal_address   => '%(CONFIG_CONTROLLER_HOST)s',
  password           => '%(CONFIG_HEAT_KS_PW)s'
}

