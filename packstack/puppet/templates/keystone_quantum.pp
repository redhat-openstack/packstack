
class {"quantum::keystone::auth":
    password    => "%(CONFIG_QUANTUM_KS_PW)s",
    public_address => "%(CONFIG_QUANTUM_SERVER_HOST)s",
    admin_address => "%(CONFIG_QUANTUM_SERVER_HOST)s",
    internal_address => "%(CONFIG_QUANTUM_SERVER_HOST)s",
}
