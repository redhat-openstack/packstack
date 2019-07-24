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
}
