class packstack::nova::compute::flat ()
{
    $nova_compute_privif = hiera('CONFIG_NOVA_COMPUTE_PRIVIF')

    $use_subnets_value = hiera('CONFIG_USE_SUBNETS')
    $use_subnets = $use_subnets_value ? {
      'y'     => true,
      default => false,
    }

    nova_config {
      'DEFAULT/flat_interface': value => force_interface($nova_compute_privif, $use_subnets);
    }
}
