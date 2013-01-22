
class {"cinder::keystone::auth":
    password => "%(CONFIG_CINDER_KS_PW)s",
    public_address => "%(CONFIG_CINDER_HOST)s",
    admin_address => "%(CONFIG_CINDER_HOST)s",
    internal_address => "%(CONFIG_CINDER_HOST)s",
}
