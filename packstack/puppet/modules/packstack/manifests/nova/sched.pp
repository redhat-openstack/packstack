class packstack::nova::sched ()
{
    class {'::nova::scheduler::filter':
      scheduler_default_filters => ['RetryFilter', 'AvailabilityZoneFilter',
                                    'ComputeFilter',
                                    'ComputeCapabilitiesFilter', 'ImagePropertiesFilter',
                                    'ServerGroupAntiAffinityFilter',
                                    'ServerGroupAffinityFilter'],
    }

    class { '::nova::scheduler':
      enabled => true,
    }

    Keystone_endpoint <||> -> Service['nova-scheduler']
    Keystone_service <||> -> Service['nova-scheduler']

}
