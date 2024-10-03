
define packstack::manila::network ($backend_name = $name) {
  $manila_network_type = lookup('CONFIG_MANILA_NETWORK_TYPE')

  case $manila_network_type {
    'neutron': {
      class { 'manila::network::neutron':
        auth_type => 'password',
        auth_url  => lookup('CONFIG_KEYSTONE_PUBLIC_URL_VERSIONLESS'),
        password  => lookup('CONFIG_NEUTRON_KS_PW'),
      }
    }
    'standalone': {
      manila::network::standalone{ $backend_name:
        standalone_network_plugin_gateway           => lookup('CONFIG_MANILA_NETWORK_STANDALONE_GATEWAY'),
        standalone_network_plugin_mask              => lookup('CONFIG_MANILA_NETWORK_STANDALONE_NETMASK'),
        standalone_network_plugin_segmentation_id   => lookup('CONFIG_MANILA_NETWORK_STANDALONE_SEG_ID'),
        standalone_network_plugin_allowed_ip_ranges => lookup('CONFIG_MANILA_NETWORK_STANDALONE_IP_RANGE'),
        standalone_network_plugin_ip_version        => lookup('CONFIG_MANILA_NETWORK_STANDALONE_IP_VERSION'),
      }
    }
    default: {
      fail("The value ${manila_network_type} is not a valid value for the Manila network type.")
    }
  }
}

