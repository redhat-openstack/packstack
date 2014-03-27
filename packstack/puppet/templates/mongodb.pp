class { 'mongodb::server':
    smallfiles   => true,
    bind_ip      => ['%(CONFIG_MONGODB_HOST)s'],
}
