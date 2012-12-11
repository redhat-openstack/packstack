
class {"nova::keystone::auth":
    password    => "nova_default_password",
    public_address => "%(CONFIG_NOVA_API_HOST)s",
    admin_address => "%(CONFIG_NOVA_API_HOST)s",
    internal_address => "%(CONFIG_NOVA_API_HOST)s",
    cinder => true,
}

