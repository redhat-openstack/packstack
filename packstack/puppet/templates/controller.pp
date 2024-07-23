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

include 'packstack::amqp'
include 'packstack::mariadb'

if lookup('CONFIG_MARIADB_INSTALL') == 'y' {
  include 'packstack::mariadb::services'
} else {
  include 'packstack::mariadb::services_remote'
}

include 'packstack::apache'
include 'packstack::keystone'

if lookup('CONFIG_GLANCE_INSTALL') == 'y' {
  include 'packstack::keystone::glance'
  include 'packstack::glance'
  if lookup('CONFIG_CEILOMETER_INSTALL') == 'y' {
    include 'packstack::glance::ceilometer'
  }
  if lookup('CONFIG_GLANCE_BACKEND') == 'swift' {
    include 'packstack::glance::backend::swift'
  } else {
    include 'packstack::glance::backend::file'
  }
}

if lookup('CONFIG_CINDER_INSTALL') == 'y' {
  include 'openstacklib::iscsid'
  include 'packstack::keystone::cinder'
  include 'packstack::cinder::rabbitmq'
  include 'packstack::cinder'
  if lookup('CONFIG_SWIFT_INSTALL') == 'y' {
    include 'packstack::cinder::backup'
  }

  $cinder_backends = lookup('CONFIG_CINDER_BACKEND', { merge => 'unique' })

  case $cinder_backends[0] {
    'lvm':       { include 'packstack::cinder::backend::lvm' }
    'nfs':       { include 'packstack::cinder::backend::nfs' }
    'vmdk':      { include 'packstack::cinder::backend::vmdk' }
    'netapp':    { include 'packstack::cinder::backend::netapp' }
    'solidfire': { include 'packstack::cinder::backend::solidfire' }
    default:     { include 'packstack::cinder::backend::lvm' }
  }
}

if lookup('CONFIG_IRONIC_INSTALL') == 'y' {
  include 'packstack::keystone::ironic'
  include 'packstack::ironic'
  include 'packstack::ironic::rabbitmq'
}

if lookup('CONFIG_NOVA_INSTALL') == 'y' {
  include 'packstack::keystone::nova'
  include 'packstack::nova'
  include 'packstack::nova::common'
  include 'packstack::nova::api'
  include 'packstack::nova::conductor'
  if lookup('CONFIG_IRONIC_INSTALL') == 'y' {
    include 'packstack::nova::sched::ironic'
  } else {
    include 'packstack::nova::sched'
  }
  include 'packstack::nova::vncproxy'
  include 'packstack::nova::neutron'
  include 'packstack::placement'
}

if lookup('CONFIG_NEUTRON_INSTALL') == 'y' {
  include 'packstack::keystone::neutron'
  include 'packstack::neutron::rabbitmq'
  include 'packstack::neutron::api'
  if lookup('CONFIG_NOVA_INSTALL') == 'y' {
    include 'packstack::neutron::notifications'
  }
  include 'packstack::neutron::ml2'
  if lookup('CONFIG_NEUTRON_L2_AGENT') == 'ovn' {
    include 'packstack::neutron::ovn_northd'
  }
}

if lookup('CONFIG_MANILA_INSTALL') == 'y' {
  include 'packstack::keystone::manila'
  include 'packstack::manila'
  include 'packstack::manila::rabbitmq'
  if 'generic' in lookup('CONFIG_MANILA_BACKEND', { merge => 'unique' }) {
    include 'packstack::manila::backend::generic'
  }
  if 'netapp' in lookup('CONFIG_MANILA_BACKEND', { merge => 'unique' }) {
    include 'packstack::manila::backend::netapp'
  }
  if 'glusternative' in lookup('CONFIG_MANILA_BACKEND', { merge => 'unique' }) {
    include 'packstack::manila::backend::glusternative'
  }
  if 'glusternfs' in lookup('CONFIG_MANILA_BACKEND', { merge => 'unique' }) {
    include 'packstack::manila::backend::glusternfs'
  }
}

include 'packstack::openstackclient'

if lookup('CONFIG_HORIZON_INSTALL') == 'y' {
  include 'packstack::horizon'
}

if lookup('CONFIG_SWIFT_INSTALL') == 'y' {
  include 'packstack::keystone::swift'
  include 'packstack::swift'
  include 'packstack::swift::ringbuilder'
  include 'packstack::swift::proxy'
  include 'packstack::swift::storage'
  if lookup('CONFIG_CEILOMETER_INSTALL') == 'y' and
     lookup('CONFIG_ENABLE_CEILOMETER_MIDDLEWARE') == 'y' {
    include 'packstack::swift::ceilometer'
  }
}

if lookup('CONFIG_HEAT_INSTALL') == 'y' {
  include 'packstack::keystone::heat'
  include 'packstack::heat::rabbitmq'
  include 'packstack::heat'
  if lookup('CONFIG_HEAT_CFN_INSTALL') == 'y' {
    include 'packstack::heat::cfn'
  }
}

if lookup('CONFIG_MAGNUM_INSTALL') == 'y' {
  include 'packstack::keystone::magnum'
  include 'packstack::magnum'
  include 'packstack::magnum::rabbitmq'
}

if lookup('CONFIG_PROVISION_DEMO') == 'y' or lookup('CONFIG_PROVISION_TEMPEST') == 'y' {
  include 'packstack::provision'
  if lookup('CONFIG_GLANCE_INSTALL') == 'y' {
    include 'packstack::provision::glance'
  }
}

if lookup('CONFIG_PROVISION_TEMPEST') == 'y' {
  include 'packstack::provision::tempest'
}


if lookup('CONFIG_PROVISION_TEMPEST') == 'y' {
  include 'packstack::provision::tempest'
}


if lookup('CONFIG_CEILOMETER_INSTALL') == 'y' {
  # setup gnocchi
  include 'packstack::keystone::gnocchi'
  include 'packstack::gnocchi'
  # setup ceilometer
  include 'packstack::keystone::ceilometer'
  include 'packstack::ceilometer::rabbitmq'
  include 'packstack::ceilometer'
  if lookup('CONFIG_NOVA_INSTALL') == 'n' {
    include 'packstack::ceilometer::nova_disabled'
  }
  include 'packstack::redis'
}

if lookup('CONFIG_CEILOMETER_INSTALL') == 'y' and lookup('CONFIG_AODH_INSTALL') == 'y' {
  include 'packstack::keystone::aodh'
  include 'packstack::aodh::rabbitmq'
  include 'packstack::aodh'
}

if lookup('CONFIG_TROVE_INSTALL') == 'y' {
  include 'packstack::keystone::trove'
  include 'packstack::trove::rabbitmq'
  include 'packstack::trove'
}
