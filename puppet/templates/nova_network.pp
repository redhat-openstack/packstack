
class {"nova::network":
    enabled => true,
    private_interface => '%(CONFIG_NOVANETWORK_PRIVIF)s',
    public_interface => '%(CONFIG_NOVANETWORK_PUBIF)s',
    fixed_range => '%(CONFIG_NOVANETWORK_FIXEDRANGE)s',
    floating_range => '%(CONFIG_NOVANETWORK_FLOATINGRANGE)s'
}
