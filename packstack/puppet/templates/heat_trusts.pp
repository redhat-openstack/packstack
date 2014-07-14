
heat_config {
  'DEFAULT/deferred_auth_method'   : value => 'trusts';
  'DEFAULT/trusts_delegated_roles' : value => 'heat_stack_owner';
}

keystone_user_role { 'admin@admin':
  ensure => present,
  roles  => ['admin', '_member_', 'heat_stack_owner'],
}
