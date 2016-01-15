
$multihost = hiera('CONFIG_NOVA_NETWORK_MULTIHOST')
if $multihost {
  nova_config {
    'DEFAULT/send_arp_for_ha': value => true;
  }
}

$manager = hiera('CONFIG_NOVA_NETWORK_MANAGER')

$nova_net_manager_list = [
  'nova.network.manager.VlanManager',
  'nova.network.manager.FlatDHCPManager',
]

$overrides = {}

if $manager in $nova_net_manager_list {
  $overrides['force_dhcp_release'] = false
}

if $manager == 'nova.network.manager.VlanManager' {
  $overrides['vlan_start'] = hiera('CONFIG_NOVA_NETWORK_VLAN_START')
  $net_size = hiera('CONFIG_NOVA_NETWORK_SIZE')
  $net_num = hiera('CONFIG_NOVA_NETWORK_NUMBER')
} else {
  $net_size = hiera('CONFIG_NOVA_NETWORK_FIXEDSIZE')
  $net_num = 1
}

$nova_network_privif = hiera('CONFIG_NOVA_NETWORK_PRIVIF')
$nova_network_pubif = hiera('CONFIG_NOVA_NETWORK_PUBIF')

class { '::nova::network':
  enabled                 => true,
  network_manager         => $manager,
  num_networks            => $net_num ,
  network_size            => $net_size,
  private_interface       => force_interface($nova_network_privif, $use_subnets),
  public_interface        => force_interface($nova_network_pubif, $use_subnets),
  fixed_range             => hiera('CONFIG_NOVA_NETWORK_FIXEDRANGE'),
  floating_range          => hiera('CONFIG_NOVA_NETWORK_FLOATRANGE'),
  config_overrides        => $overrides,
  auto_assign_floating_ip => hiera('CONFIG_NOVA_NETWORK_AUTOASSIGNFLOATINGIP'),
  multi_host              => $multihost
}

package { 'dnsmasq':
  ensure => present,
}
