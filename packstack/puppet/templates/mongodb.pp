$mongodb_host = hiera('CONFIG_MONGODB_HOST')

class { '::mongodb::server':
  ipv6       => hiera('CONFIG_IP_VERSION') ? {
    'ipv6'  => true,
    default => false,
  },
  smallfiles => true,
  bind_ip    => $mongodb_host,
}

