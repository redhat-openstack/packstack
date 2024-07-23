stage { "init": before  => Stage["main"] }

Exec { timeout => lookup('DEFAULT_EXEC_TIMEOUT') }
Package { allow_virtual => true }

class { 'packstack::prereqs':
  stage => init,
}

include firewall

create_resources(sshkey, lookup('SSH_KEYS', undef, undef, {}))

if lookup('CONFIG_NTP_SERVERS', undef, undef, '') != '' {
  include 'packstack::chrony'
}

if lookup('CONFIG_CEILOMETER_INSTALL') == 'y' {
  include 'packstack::nova::ceilometer::rabbitmq'
  include 'packstack::nova::ceilometer'
}

include 'packstack::nova'
include 'packstack::nova::common'
include 'packstack::nova::compute'

if lookup('CONFIG_VMWARE_BACKEND') == 'y' {
  include 'packstack::nova::compute::vmware'
} elsif lookup('CONFIG_IRONIC_INSTALL') == 'y' {
  include 'packstack::nova::compute::ironic'
} else {
  include 'packstack::nova::compute::libvirt'
}

if lookup('CONFIG_CINDER_INSTALL') == 'y' {
  include 'openstacklib::iscsid'
}

if lookup('CONFIG_CINDER_INSTALL') == 'y' and
   lookup('CONFIG_VMWARE_BACKEND') != 'y' {
   if 'nfs' in lookup('CONFIG_CINDER_BACKEND', { merge => 'unique' }) {
    include 'packstack::nova::nfs'
   }
}

include 'packstack::nova::neutron'
include 'packstack::neutron::rabbitmq'
case lookup('CONFIG_NEUTRON_L2_AGENT') {
  'openvswitch': { include 'packstack::neutron::ovs_agent' }
  'linuxbridge': { include 'packstack::neutron::lb_agent' }
  'ovn':         { include 'packstack::neutron::ovn_agent'
                   include 'packstack::neutron::ovn_metadata'
                 }
  default:       { include 'packstack::neutron::ovs_agent' }
}
include 'packstack::neutron::bridge'

if 'sriovnicswitch' in lookup('CONFIG_NEUTRON_ML2_MECHANISM_DRIVERS', { merge => 'unique' }) and
   lookup('CONFIG_NEUTRON_L2_AGENT') == 'openvswitch' {
  include 'packstack::neutron::sriov'
}
