
class {"glance::keystone::auth":
    password => "glance_default_password",
    public_address => "%(CONFIG_GLANCE_HOST)s",
    admin_address => "%(CONFIG_GLANCE_HOST)s",
    internal_address => "%(CONFIG_GLANCE_HOST)s",
}

