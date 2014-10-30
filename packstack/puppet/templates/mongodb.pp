$mongodb_host = hiera('CONFIG_MONGODB_HOST')

class { 'mongodb::server':
  smallfiles => true,
  bind_ip    => [$mongodb_host],
}

