stage { "init": before  => Stage["main"] }

Exec { timeout => hiera('DEFAULT_EXEC_TIMEOUT') }
Package { allow_virtual => true }

class {'::packstack::prereqs':
  stage => init,
}

if hiera('CONFIG_NTP_SERVERS', undef) != undef {
  include '::packstack::chrony'
}

if hiera('CONFIG_NEUTRON_INSTALL') == 'y' {
  include '::packstack::neutron::rabbitmq'

  if hiera('CONFIG_NEUTRON_VPNAAS') == 'y' {
    include '::packstack::neutron::vpnaas'
  }
  if hiera('CONFIG_NEUTRON_FWAAS') == 'y' {
    include '::packstack::neutron::fwaas'
  }
  if hiera('CONFIG_LBAAS_INSTALL') == 'y' {
    include '::packstack::neutron::lbaas'
  }
  include '::packstack::neutron::l3'
  if hiera('CONFIG_NEUTRON_OVS_BRIDGE_CREATE') == 'y' {
    include '::packstack::neutron::ovs_bridge'
  }

  case hiera('CONFIG_NEUTRON_L2_AGENT') {
    'openvswitch': { include '::packstack::neutron::ovs_agent' }
    'linuxbridge': { include '::packstack::neutron::lb_agent' }
    default:       { include '::packstack::neutron::ovs_agent' }
  }
  include '::packstack::neutron::bridge'
  include '::packstack::neutron::dhcp'
  if hiera('CONFIG_NEUTRON_METERING_AGENT_INSTALL') == 'y' {
    include '::packstack::neutron::metering'
  }
  if hiera('CONFIG_NOVA_INSTALL') == 'y' {
    include '::packstack::neutron::metadata'
  }

  if hiera('CONFIG_PROVISION_DEMO') == 'y' or hiera('CONFIG_PROVISION_TEMPEST') == 'y' {
    include '::packstack::provision::bridge'
  }
}

if hiera('CONFIG_NAGIOS_INSTALL') == 'y' {
  include '::packstack::nagios::nrpe'
}
