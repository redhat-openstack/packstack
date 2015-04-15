
$nova_compute_privif = hiera('CONFIG_NOVA_COMPUTE_PRIVIF')

nova_config {
  'DEFAULT/flat_interface': value => force_interface($nova_compute_privif, $use_subnets);
}
