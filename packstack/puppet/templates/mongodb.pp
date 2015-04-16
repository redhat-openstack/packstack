$mongodb_host = hiera('CONFIG_MONGODB_HOST')
$use_epel = hiera('CONFIG_USE_EPEL')

# The MongoDB config files differ between versions
if (($::operatingsystem == 'fedora' and versioncmp($::operatingsystemrelease, '22') >= 0)
    or
    ($::operatingsystem != 'fedora' and versioncmp($::operatingsystemrelease, '7.0') >= 0 and $use_epel == 'y')
   ){
  $config_file = '/etc/mongod.conf'
} else {
  $config_file = '/etc/mongodb.conf'
}

class { '::mongodb::server':
  ipv6       => hiera('CONFIG_IP_VERSION') ? {
    'ipv6'  => true,
    default => false,
  },
  smallfiles => true,
  bind_ip    => $mongodb_host,
  config     => $config_file,
}

