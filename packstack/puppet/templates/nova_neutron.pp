
class {"nova::network::neutron":
  neutron_admin_password => "%(CONFIG_NEUTRON_KS_PW)s",
  neutron_auth_strategy => "keystone",
  neutron_url => "http://%(CONFIG_CONTROLLER_HOST)s:9696",
  neutron_admin_tenant_name => "services",
  neutron_admin_auth_url => "http://%(CONFIG_CONTROLLER_HOST)s:35357/v2.0",
  neutron_region_name => "%(CONFIG_KEYSTONE_REGION)s",
}

class {"nova::compute::neutron":
  libvirt_vif_driver => "%(CONFIG_NOVA_LIBVIRT_VIF_DRIVER)s",
}
