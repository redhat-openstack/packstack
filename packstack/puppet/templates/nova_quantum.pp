
class {"nova::network::quantum":
  quantum_admin_password => "%(CONFIG_QUANTUM_KS_PW)s",
  quantum_auth_strategy => "keystone",
  quantum_url => "http://%(CONFIG_QUANTUM_SERVER_HOST)s:9696",
  quantum_admin_tenant_name => "services",
  quantum_admin_auth_url => "http://%(CONFIG_KEYSTONE_HOST)s:35357/v2.0",
}

class {"nova::compute::quantum":
  libvirt_vif_driver => "nova.virt.libvirt.vif.LibvirtGenericVifDriver",
}

nova_config {
  'DEFAULT/service_quantum_metadata_proxy': value => 'True';
  'DEFAULT/quantum_metadata_proxy_shared_secret': value => '%(CONFIG_QUANTUM_METADATA_PW)s';
}
