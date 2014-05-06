
class {"neutron::keystone::auth":
    password    => "%(CONFIG_NEUTRON_KS_PW)s",
    public_address => "%(CONFIG_CONTROLLER_HOST)s",
    admin_address => "%(CONFIG_CONTROLLER_HOST)s",
    internal_address => "%(CONFIG_CONTROLLER_HOST)s",
}
