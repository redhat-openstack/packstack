
class {"nova::keystone::auth":
    password    => "%(CONFIG_NOVA_KS_PW)s",
    public_address => "%(CONFIG_NOVA_API_HOST)s",
    admin_address => "%(CONFIG_NOVA_API_HOST)s",
    internal_address => "%(CONFIG_NOVA_API_HOST)s",
    cinder => true,
}
