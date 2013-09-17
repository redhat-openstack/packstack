
nova_config {
    "DEFAULT/default_floating_pool": value => '%(CONFIG_NOVA_NETWORK_DEFAULTFLOATINGPOOL)s';
    "DEFAULT/auto_assign_floating_ip": value => '%(CONFIG_NOVA_NETWORK_AUTOASSIGNFLOATINGIP)s';
}

$multihost = %(CONFIG_NOVA_NETWORK_MULTIHOST)s
if $multihost {
    nova_config {
        "DEFAULT/multi_host": value => true;
        "DEFAULT/send_arp_for_ha": value => true;
    }
}

$manager = '%(CONFIG_NOVA_NETWORK_MANAGER)s'
$overrides = {}
if $manager in ['nova.network.manager.VlanManager', 'nova.network.manager.FlatDHCPManager'] {
    $overrides['force_dhcp_release'] = false
}
if $manager == 'nova.network.manager.VlanManager' {
    $overrides['vlan_start'] = '%(CONFIG_NOVA_NETWORK_VLAN_START)s'
    $net_size = '%(CONFIG_NOVA_NETWORK_SIZE)s'
    $net_num = '%(CONFIG_NOVA_NETWORK_NUMBER)s'
} else {
    $net_size = '%(CONFIG_NOVA_NETWORK_FIXEDSIZE)s'
    $net_num = 1
}
class { "nova::network":
    enabled => true,
    network_manager => $manager,
    num_networks => $net_num ,
    network_size => $net_size,
    private_interface => '%(CONFIG_NOVA_NETWORK_PRIVIF)s',
    public_interface => '%(CONFIG_NOVA_NETWORK_PUBIF)s',
    fixed_range => '%(CONFIG_NOVA_NETWORK_FIXEDRANGE)s',
    floating_range => '%(CONFIG_NOVA_NETWORK_FLOATRANGE)s',
    config_overrides => $overrides,
}

package { 'dnsmasq': ensure => present }
