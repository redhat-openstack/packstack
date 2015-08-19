
$setup_ovs_bridge        = hiera('CONFIG_PROVISION_OVS_BRIDGE')
$provision_neutron_avail = hiera('PROVISION_NEUTRON_AVAILABLE')
$public_bridge_name      = hiera('CONFIG_NEUTRON_L3_EXT_BRIDGE')

neutron_config {
  'keystone_authtoken/identity_uri':      value => hiera('CONFIG_KEYSTONE_ADMIN_URL');
  'keystone_authtoken/auth_uri':          value => hiera('CONFIG_KEYSTONE_PUBLIC_URL');
  'keystone_authtoken/admin_tenant_name': value => 'services';
  'keystone_authtoken/admin_user':        value => 'neutron';
  'keystone_authtoken/admin_password':    value => hiera('CONFIG_NEUTRON_KS_PW');
}

if $provision_neutron_avail and $setup_ovs_bridge {
  Neutron_config<||> -> Neutron_l3_ovs_bridge['demo_bridge']
  neutron_l3_ovs_bridge { 'demo_bridge':
    name        => $public_bridge_name,
    ensure      => present,
    subnet_name => 'public_subnet',
  }

  firewall { '000 nat':
    chain    => 'POSTROUTING',
    jump     => 'MASQUERADE',
    source   => hiera('CONFIG_PROVISION_DEMO_FLOATRANGE'),
    outiface => $::gateway_device,
    table    => 'nat',
    proto    => 'all',
  }

  firewall { '000 forward out':
    chain    => 'FORWARD',
    action   => 'accept',
    outiface => $public_bridge_name,
    proto    => 'all',
  }

  firewall { '000 forward in':
    chain   => 'FORWARD',
    action  => 'accept',
    iniface => $public_bridge_name,
    proto   => 'all',
  }
}
