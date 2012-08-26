
class {"nova::keystone::auth":
    public_address => "%(CONFIG_NOVA_API_HOST)s",
    admin_address => "%(CONFIG_NOVA_API_HOST)s",
    internal_address => "%(CONFIG_NOVA_API_HOST)s",
}

