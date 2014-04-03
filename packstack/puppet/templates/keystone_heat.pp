# heat::keystone::auth
class {"heat::keystone::auth":
    password => "%(CONFIG_HEAT_KS_PW)s",
    public_address => "%(CONFIG_HEAT_HOST)s",
    admin_address => "%(CONFIG_HEAT_HOST)s",
    internal_address => "%(CONFIG_HEAT_HOST)s",
}

if '%(CONFIG_HEAT_CFN_INSTALL)s' == 'y' {
    # heat::keystone::cfn
    class {"heat::keystone::auth_cfn":
        password => "%(CONFIG_HEAT_KS_PW)s",
        public_address => "%(CONFIG_HEAT_HOST)s",
        admin_address => "%(CONFIG_HEAT_HOST)s",
        internal_address => "%(CONFIG_HEAT_HOST)s",
    }
}
