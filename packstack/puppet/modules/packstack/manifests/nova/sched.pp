class packstack::nova::sched ()
{
    class {'::nova::scheduler::filter':
      # OpenStack doesn't include the CoreFilter (= CPU Filter) by default
      scheduler_default_filters => ['RetryFilter', 'AvailabilityZoneFilter',
                                    'RamFilter', 'DiskFilter' , 'ComputeFilter',
                                    'ComputeCapabilitiesFilter', 'ImagePropertiesFilter',
                                    'ServerGroupAntiAffinityFilter',
                                    'ServerGroupAffinityFilter', 'CoreFilter'],
    }

    class { '::nova::scheduler':
      enabled => true,
    }
}
