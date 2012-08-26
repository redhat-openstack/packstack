
class {"nova::network":
    enabled => true,
    private_interface => '%(CONFIG_NOVA_NETWORK_PRIVIF)s',
    public_interface => '%(CONFIG_NOVA_NETWORK_PUBIF)s',
    fixed_range => '%(CONFIG_NOVA_NETWORK_FIXEDRANGE)s',
    floating_range => '%(CONFIG_NOVA_NETWORK_FLOATINGRANGE)s'
}
