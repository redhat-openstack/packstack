class packstack::nova::sched ()
{
    class {'::nova::scheduler::filter':
      # OpenStack doesn't include the CoreFilter (= CPU Filter) by default
      scheduler_default_filters => ['RetryFilter', 'AvailabilityZoneFilter',
                                    'RamFilter', 'DiskFilter' , 'ComputeFilter',
                                    'ComputeCapabilitiesFilter', 'ImagePropertiesFilter',
                                    'ServerGroupAntiAffinityFilter',
                                    'ServerGroupAffinityFilter', 'CoreFilter'],
      cpu_allocation_ratio      => hiera('CONFIG_NOVA_SCHED_CPU_ALLOC_RATIO'),
      ram_allocation_ratio      => hiera('CONFIG_NOVA_SCHED_RAM_ALLOC_RATIO'),
    }

    class { '::nova::scheduler':
      enabled => true,
    }
}
