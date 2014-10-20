
class {"cinder::keystone::auth":
    password         => "%(CONFIG_CINDER_KS_PW)s",
    public_address   => "%(CONFIG_STORAGE_HOST)s",
    admin_address    => "%(CONFIG_STORAGE_HOST)s",
    internal_address => "%(CONFIG_STORAGE_HOST)s",
}

