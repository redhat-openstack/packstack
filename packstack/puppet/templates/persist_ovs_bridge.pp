$persist_ovs_br_neut_l3_ext_br = hiera('CONFIG_NEUTRON_L3_EXT_BRIDGE')
$persist_ovs_br_ext_br_var     = hiera('EXT_BRIDGE_VAR')

$net_script = "DEVICE=${persist_ovs_br_neut_l3_ext_br}
DEVICETYPE=ovs
TYPE=OVSBridge
BOOTPROTO=static
IPADDR=${ipaddress}_${persist_ovs_br_ext_br_var}
NETMASK=${netmask}_${persist_ovs_br_ext_br_var}
ONBOOT=yes"

file { "/etc/sysconfig/network-scripts/ifcfg-${persist_ovs_br_neut_l3_ext_br}":
  content => $net_script,
}
