class packstack::nova::sched::ironic ()
{
    nova_config {
      'DEFAULT/scheduler_host_manager':
        value => 'ironic_host_manager';
    }
}
