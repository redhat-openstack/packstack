
class {"glance::keystone::auth":
    public_address => "%(CONFIG_GLANCE_HOST)s",
    admin_address => "%(CONFIG_GLANCE_HOST)s",
    internal_address => "%(CONFIG_GLANCE_HOST)s",
}

