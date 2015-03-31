nova_config{
  # OpenStack doesn't include the CoreFilter (= CPU Filter) by default
  'DEFAULT/scheduler_default_filters':
      value => 'RetryFilter,AvailabilityZoneFilter,RamFilter,ComputeFilter,ComputeCapabilitiesFilter,ImagePropertiesFilter,CoreFilter';
  'DEFAULT/cpu_allocation_ratio':
      value => hiera('CONFIG_NOVA_SCHED_CPU_ALLOC_RATIO');
  'DEFAULT/ram_allocation_ratio':
      value => hiera('CONFIG_NOVA_SCHED_RAM_ALLOC_RATIO');
}

class { '::nova::scheduler':
  enabled => true,
}
