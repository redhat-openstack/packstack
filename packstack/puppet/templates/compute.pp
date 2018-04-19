stage { "init": before  => Stage["main"] }

Exec { timeout => hiera('DEFAULT_EXEC_TIMEOUT') }
Package { allow_virtual => true }

class {'::packstack::prereqs':
  stage => init,
}

include ::firewall

create_resources(sshkey, hiera('SSH_KEYS', {}))

if hiera('CONFIG_NTP_SERVERS', '') != '' {
  include '::packstack::chrony'
}

if hiera('CONFIG_CEILOMETER_INSTALL') == 'y' {
  include '::packstack::nova::ceilometer::rabbitmq'
  include '::packstack::nova::ceilometer'
}

include '::packstack::nova'
include '::packstack::nova::common'
include '::packstack::nova::compute'

if hiera('CONFIG_VMWARE_BACKEND') == 'y' {
  include '::packstack::nova::compute::vmware'
} elsif hiera('CONFIG_IRONIC_INSTALL') == 'y' {
  include '::packstack::nova::compute::ironic'
} else {
  include '::packstack::nova::compute::libvirt'
}

if hiera('CONFIG_CINDER_INSTALL') == 'y' and
   hiera('CONFIG_VMWARE_BACKEND') != 'y' {
   if 'gluster' in hiera_array('CONFIG_CINDER_BACKEND') {
    include '::packstack::nova::gluster'
   }
   if 'nfs' in hiera_array('CONFIG_CINDER_BACKEND') {
    include '::packstack::nova::nfs'
   }
}

if hiera('CONFIG_NEUTRON_INSTALL') == 'y' {
  include '::packstack::nova::neutron'
  include '::packstack::neutron::rabbitmq'
  case hiera('CONFIG_NEUTRON_L2_AGENT') {
    'openvswitch': { include '::packstack::neutron::ovs_agent' }
    'linuxbridge': { include '::packstack::neutron::lb_agent' }
    'ovn':         { include '::packstack::neutron::ovn_agent'
                     include '::packstack::neutron::ovn_metadata'
                   }
    default:       { include '::packstack::neutron::ovs_agent' }
  }
  include '::packstack::neutron::bridge'

  if 'sriovnicswitch' in hiera_array('CONFIG_NEUTRON_ML2_MECHANISM_DRIVERS') and
     hiera ('CONFIG_NEUTRON_L2_AGENT') == 'openvswitch' {
    include '::packstack::neutron::sriov'
  }
}
