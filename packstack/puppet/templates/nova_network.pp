nova_config{
    "DEFAULT/default_floating_pool": value => '%(CONFIG_NOVA_NETWORK_DEFAULTFLOATINGPOOL)s';
    "DEFAULT/auto_assign_floating_ip": value => '%(CONFIG_NOVA_NETWORK_AUTOASSIGNFLOATINGIP)s';
}

class {"nova::network":
    enabled => true,
    private_interface => '%(CONFIG_NOVA_NETWORK_PRIVIF)s',
    public_interface => '%(CONFIG_NOVA_NETWORK_PUBIF)s',
    fixed_range => '%(CONFIG_NOVA_NETWORK_FIXEDRANGE)s',
    network_size => '%(CONFIG_NOVA_NETWORK_FIXEDSIZE)s',
    floating_range => '%(CONFIG_NOVA_NETWORK_FLOATRANGE)s',
    config_overrides => {force_dhcp_release => false}
}

package { 'dnsmasq': ensure => present }
