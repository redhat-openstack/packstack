class packstack::nova::sched::ironic ()
{
  class { 'nova::scheduler':
    enabled => true,
  }
}