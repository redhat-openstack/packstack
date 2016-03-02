class { '::glance::backend::swift':
  swift_store_user                    => 'services:glance',
  swift_store_key                     => hiera('CONFIG_GLANCE_KS_PW'),
  swift_store_auth_address            => hiera('CONFIG_KEYSTONE_PUBLIC_URL'),
  swift_store_container               => 'glance',
  swift_store_auth_version            => '2',
  swift_store_large_object_size       => '5120',
  swift_store_create_container_on_put => true,
}
