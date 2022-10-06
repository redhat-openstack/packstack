stage { "init": before  => Stage["main"] }

Exec { timeout => lookup('DEFAULT_EXEC_TIMEOUT') }
Package { allow_virtual => true }

class { 'packstack::prereqs':
  stage => init,
}

include firewall

if lookup('CONFIG_NTP_SERVERS', undef, undef, '') != '' {
  include 'packstack::chrony'
}

if lookup('CONFIG_NEUTRON_INSTALL') == 'y' {
  include 'packstack::neutron::rabbitmq'

  if lookup('CONFIG_NEUTRON_VPNAAS') == 'y' {
    include 'packstack::neutron::vpnaas'
  }
  if lookup('CONFIG_NEUTRON_L2_AGENT') != 'ovn' {
    include 'packstack::neutron::l3'
  }
  if lookup('CONFIG_NEUTRON_OVS_BRIDGE_CREATE') == 'y' {
    include 'packstack::neutron::ovs_bridge'
  }

  case lookup('CONFIG_NEUTRON_L2_AGENT') {
    'openvswitch': { include 'packstack::neutron::ovs_agent' }
    'linuxbridge': { include 'packstack::neutron::lb_agent' }
    'ovn':         { include 'packstack::neutron::ovn_agent' }
    default:       { include 'packstack::neutron::ovs_agent' }
  }
  include 'packstack::neutron::bridge'
  if lookup('CONFIG_NEUTRON_L2_AGENT') != 'ovn' {
    include 'packstack::neutron::dhcp'
    include 'packstack::neutron::metadata'
  }
  if lookup('CONFIG_NEUTRON_METERING_AGENT_INSTALL') == 'y' {
    include 'packstack::neutron::metering'
  }
  if lookup('CONFIG_PROVISION_DEMO') == 'y' or lookup('CONFIG_PROVISION_TEMPEST') == 'y' {
    include 'packstack::provision::bridge'
  }
}
