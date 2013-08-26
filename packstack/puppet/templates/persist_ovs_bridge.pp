$net_script = "DEVICE=%(CONFIG_NEUTRON_L3_EXT_BRIDGE)s
DEVICETYPE=ovs
TYPE=OVSBridge
BOOTPROTO=static
IPADDR=$ipaddress_%(EXT_BRIDGE_VAR)s
NETMASK=$netmask_%(EXT_BRIDGE_VAR)s
ONBOOT=yes"

file { "/etc/sysconfig/network-scripts/ifcfg-%(CONFIG_NEUTRON_L3_EXT_BRIDGE)s":
  content => $net_script
}
