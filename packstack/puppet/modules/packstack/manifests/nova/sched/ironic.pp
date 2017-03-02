class packstack::nova::sched::ironic ()
{
  class {'::nova::scheduler::filter':
    scheduler_host_manager => 'ironic_host_manager',
  }

  class { '::nova::scheduler':
    enabled => true,
  }
}