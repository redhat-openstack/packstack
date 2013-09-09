
if '%(CONFIG_HEAT_CFN_INSTALL)s' == 'y' {
    class {"heat::keystone::auth":
        password => "%(CONFIG_HEAT_KS_PW)s",
        heat_public_address => "%(CONFIG_HEAT_HOST)s",
        heat_admin_address => "%(CONFIG_HEAT_HOST)s",
        heat_internal_address => "%(CONFIG_HEAT_HOST)s",
        cfn_public_address => "%(CONFIG_HEAT_HOST)s",
        cfn_admin_address => "%(CONFIG_HEAT_HOST)s",
        cfn_internal_address => "%(CONFIG_HEAT_HOST)s",
    }
} else {
    class {"heat::keystone::auth":
        password => "%(CONFIG_HEAT_KS_PW)s",
        heat_public_address => "%(CONFIG_HEAT_HOST)s",
        heat_admin_address => "%(CONFIG_HEAT_HOST)s",
        heat_internal_address => "%(CONFIG_HEAT_HOST)s",
        cfn_auth_name => undef,
    }
}
