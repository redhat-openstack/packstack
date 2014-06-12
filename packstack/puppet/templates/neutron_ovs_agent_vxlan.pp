
if "%(CONFIG_NEUTRON_OVS_TUNNEL_IF)s" {
  $iface = regsubst('%(CONFIG_NEUTRON_OVS_TUNNEL_IF)s', '[\.\-\:]', '_', 'G')
  $localip = inline_template("<%%= scope.lookupvar('::ipaddress_${iface}') %%>")
} else {
  $localip = '%(CONFIG_NEUTRON_OVS_HOST)s'
}

class { 'neutron::agents::ovs':
  bridge_mappings => %(CONFIG_NEUTRON_OVS_BRIDGE_MAPPINGS)s,
  enable_tunneling => true,
  tunnel_types => ['vxlan'],
  local_ip => $localip,
  vxlan_udp_port => %(CONFIG_NEUTRON_OVS_VXLAN_UDP_PORT)s,
}

file { 'ovs_neutron_plugin.ini':
    path  => '/etc/neutron/plugins/openvswitch/ovs_neutron_plugin.ini',
    owner => 'root',
    group => 'neutron',
    before => Service['ovs-cleanup-service'],
    require => Package['neutron-plugin-ovs'],
}
