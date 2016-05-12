class { '::sahara::notify':
  enable_notifications => true,
  notification_driver  => 'messagingv2',
}


