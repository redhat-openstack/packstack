class packstack::sahara::ceilometer ()
{
    class { '::sahara::notify':
      notification_driver  => 'messagingv2',
    }
}
