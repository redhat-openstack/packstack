
class {"nova::network":
    enabled => true,
    private_interface => '$(CONFIG_NOVANETWORK_PRIVIF)s',
    public_interface => 'eth0',
    fixed_range => '192.168.11.0/24',
    floating_range => '192.168.13.0/24'
}
