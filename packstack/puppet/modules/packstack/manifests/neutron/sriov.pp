class packstack::neutron::sriov ()
{
    class { 'neutron::agents::ml2::sriov' :
      physical_device_mappings => lookup('CONFIG_NEUTRON_ML2_SRIOV_INTERFACE_MAPPINGS', { merge => 'unique' }),
    }
}
