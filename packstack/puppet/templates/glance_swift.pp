
class { 'glance::backend::swift':
  swift_store_user                    => 'services:glance',
  swift_store_key                     => '%(CONFIG_GLANCE_KS_PW)s',
  swift_store_auth_address            => 'http://%(CONFIG_CONTROLLER_HOST)s:35357/v2.0/',
  swift_store_container               => 'glance',
  swift_store_auth_version            => '2',
  swift_store_large_object_size       => '5120',
  swift_store_create_container_on_put => true
}
