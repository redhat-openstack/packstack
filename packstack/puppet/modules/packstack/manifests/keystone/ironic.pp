class packstack::keystone::ironic ()
{
    $ironic_protocol = 'http'
    $ironic_host = hiera('CONFIG_KEYSTONE_HOST_URL')
    $ironic_port = '6385'
    $ironic_url = "${ironic_protocol}://${ironic_host}:$ironic_port"

    class { '::ironic::keystone::auth':
        region       => hiera('CONFIG_KEYSTONE_REGION'),
        password     => hiera('CONFIG_IRONIC_KS_PW'),
        public_url   => $ironic_url,
        admin_url    => $ironic_url,
        internal_url => $ironic_url,
    }
}
