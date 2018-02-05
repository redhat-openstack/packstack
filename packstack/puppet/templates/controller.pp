stage { "init": before  => Stage["main"] }

Exec { timeout => hiera('DEFAULT_EXEC_TIMEOUT') }
Package { allow_virtual => true }

class {'::packstack::prereqs':
  stage => init,
}

include ::firewall

if hiera('CONFIG_NTP_SERVERS', '') != '' {
  include '::packstack::chrony'
}

include '::packstack::amqp'
include '::packstack::mariadb'

if hiera('CONFIG_MARIADB_INSTALL') == 'y' {
  include 'packstack::mariadb::services'
} else {
  include 'packstack::mariadb::services_remote'
}

include '::packstack::apache'
include '::packstack::keystone'

if hiera('CONFIG_GLANCE_INSTALL') == 'y' {
  include '::packstack::keystone::glance'
  include '::packstack::glance'
  if hiera('CONFIG_CEILOMETER_INSTALL') == 'y' {
    include '::packstack::glance::ceilometer'
  }
  if hiera('CONFIG_GLANCE_BACKEND') == 'swift' {
    include '::packstack::glance::backend::swift'
  } else {
    include '::packstack::glance::backend::file'
  }
}

if hiera('CONFIG_CINDER_INSTALL') == 'y' {
  include '::packstack::keystone::cinder'
  include '::packstack::cinder::rabbitmq'
  include '::packstack::cinder'
  if hiera('CONFIG_CEILOMETER_INSTALL') == 'y' {
    include '::packstack::cinder::ceilometer'
  }
  if hiera('CONFIG_SWIFT_INSTALL') == 'y' {
    include '::packstack::cinder::backup'
  }

  $cinder_backends = hiera_array('CONFIG_CINDER_BACKEND')

  case $cinder_backends[0] {
    'lvm':       { include '::packstack::cinder::backend::lvm' }
    'gluster':   { include '::packstack::cinder::backend::gluster' }
    'nfs':       { include '::packstack::cinder::backend::nfs' }
    'vmdk':      { include '::packstack::cinder::backend::vmdk' }
    'netapp':    { include '::packstack::cinder::backend::netapp' }
    'solidfire': { include '::packstack::cinder::backend::solidfire' }
    default:     { include '::packstack::cinder::backend::lvm' }
  }
}

if hiera('CONFIG_IRONIC_INSTALL') == 'y' {
  include '::packstack::keystone::ironic'
  include '::packstack::ironic'
  include '::packstack::ironic::rabbitmq'
}

if hiera('CONFIG_NOVA_INSTALL') == 'y' {
  include '::packstack::keystone::nova'
  include '::packstack::nova'
  include '::packstack::nova::common'
  include '::packstack::nova::api'
  include '::packstack::nova::conductor'
  if hiera('CONFIG_IRONIC_INSTALL') == 'y' {
    include '::packstack::nova::sched::ironic'
  } else {
    include '::packstack::nova::sched'
  }
  include '::packstack::nova::vncproxy'
  if hiera('CONFIG_NEUTRON_INSTALL') == 'y' {
    include '::packstack::nova::neutron'
  }
}

if hiera('CONFIG_NEUTRON_INSTALL') == 'y' {
  include '::packstack::keystone::neutron'
  include '::packstack::neutron::rabbitmq'
  include '::packstack::neutron::api'
  if hiera('CONFIG_NOVA_INSTALL') == 'y' {
    include '::packstack::neutron::notifications'
  }
  include '::packstack::neutron::ml2'
  if hiera('CONFIG_NEUTRON_L2_AGENT') == 'ovn' {
    include '::packstack::neutron::ovn_northd'
  }
}

if hiera('CONFIG_MANILA_INSTALL') == 'y' {
  include '::packstack::keystone::manila'
  include '::packstack::manila'
  include '::packstack::manila::rabbitmq'
  if 'generic' in hiera_array('CONFIG_MANILA_BACKEND') {
    include '::packstack::manila::backend::generic'
  }
  if 'netapp' in hiera_array('CONFIG_MANILA_BACKEND') {
    include '::packstack::manila::backend::netapp'
  }
  if 'glusternative' in hiera_array('CONFIG_MANILA_BACKEND') {
    include '::packstack::manila::backend::glusternative'
  }
  if 'glusternfs' in hiera_array('CONFIG_MANILA_BACKEND') {
    include '::packstack::manila::backend::glusternfs'
  }
}

include '::packstack::openstackclient'

if hiera('CONFIG_HORIZON_INSTALL') == 'y' {
  include '::packstack::horizon'
}

if hiera('CONFIG_SWIFT_INSTALL') == 'y' {
  include '::packstack::keystone::swift'
  include '::packstack::swift'
  include '::packstack::swift::ringbuilder'
  include '::packstack::swift::proxy'
  include '::packstack::swift::storage'
  if hiera('CONFIG_CEILOMETER_INSTALL') == 'y' and
     hiera('CONFIG_ENABLE_CEILOMETER_MIDDLEWARE') == 'y' {
    include '::packstack::swift::ceilometer'
  }
}

if hiera('CONFIG_HEAT_INSTALL') == 'y' {
  include '::packstack::keystone::heat'
  include '::packstack::heat::rabbitmq'
  include '::packstack::heat'
  if hiera('CONFIG_HEAT_CFN_INSTALL') == 'y' {
    include '::packstack::heat::cfn'
  }
}

if hiera('CONFIG_MAGNUM_INSTALL') == 'y' {
  include '::packstack::keystone::magnum'
  include '::packstack::magnum'
  include '::packstack::magnum::rabbitmq'
}

if hiera('CONFIG_PROVISION_DEMO') == 'y' or hiera('CONFIG_PROVISION_TEMPEST') == 'y' {
  include '::packstack::provision'
  if hiera('CONFIG_GLANCE_INSTALL') == 'y' {
    include '::packstack::provision::glance'
  }
}

if hiera('CONFIG_PROVISION_TEMPEST') == 'y' {
  include '::packstack::provision::tempest'
}


if hiera('CONFIG_PROVISION_TEMPEST') == 'y' {
  include '::packstack::provision::tempest'
}


if hiera('CONFIG_CEILOMETER_INSTALL') == 'y' and hiera('CONFIG_PANKO_INSTALL') == 'y' {
  include '::packstack::keystone::panko'
  include '::packstack::panko'
}

if hiera('CONFIG_CEILOMETER_INSTALL') == 'y' {
  # setup gnocchi
  include '::packstack::keystone::gnocchi'
  include '::packstack::gnocchi'
  # setup ceilometer
  include '::packstack::keystone::ceilometer'
  include '::packstack::ceilometer::rabbitmq'
  include '::packstack::ceilometer'
  if hiera('CONFIG_NOVA_INSTALL') == 'n' {
    include '::packstack::ceilometer::nova_disabled'
  }
  include '::packstack::redis'
}

if hiera('CONFIG_CEILOMETER_INSTALL') == 'y' and hiera('CONFIG_AODH_INSTALL') == 'y' {
  include '::packstack::keystone::aodh'
  include '::packstack::aodh::rabbitmq'
  include '::packstack::aodh'
}

if hiera('CONFIG_TROVE_INSTALL') == 'y' {
  include '::packstack::keystone::trove'
  include '::packstack::trove::rabbitmq'
  include '::packstack::trove'
}

if hiera('CONFIG_SAHARA_INSTALL') == 'y' {
  include '::packstack::keystone::sahara'
  include '::packstack::sahara::rabbitmq'
  include '::packstack::sahara'
  if hiera('CONFIG_CEILOMETER_INSTALL') == 'y' {
    include '::packstack::sahara::ceilometer'
  }
}
