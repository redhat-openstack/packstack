
class {"nova::network::quantum":
  quantum_admin_password => "%(CONFIG_QUANTUM_KS_PW)s",
  quantum_auth_strategy => "keystone",
  quantum_url => "http://%(CONFIG_QUANTUM_SERVER_HOST)s:9696",
  quantum_admin_tenant_name => "services",
  quantum_admin_auth_url => "http://%(CONFIG_KEYSTONE_HOST)s:35357/v2.0",
}

class {"nova::compute::quantum":
  libvirt_vif_driver => "%(CONFIG_NOVA_LIBVIRT_VIF_DRIVER)s",
}
