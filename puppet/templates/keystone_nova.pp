
class {"nova::keystone::auth":
    public_address => "%(CONFIG_NOVAAPI_HOST)s",
    admin_address => "%(CONFIG_NOVAAPI_HOST)s",
    internal_address => "%(CONFIG_NOVAAPI_HOST)s",
}

