class packstack::neutron::sriov ()
{
    class { 'neutron::agents::ml2::sriov' :
      physical_device_mappings   => hiera_array('CONFIG_NEUTRON_ML2_SRIOV_INTERFACE_MAPPINGS'),
    }
}
