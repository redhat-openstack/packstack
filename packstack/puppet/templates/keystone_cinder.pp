
class {"cinder::keystone::auth":
    password => "%(CONFIG_CINDER_KS_PW)s",
    public_address => "%(CONFIG_CINDER_HOST)s",
    admin_address => "%(CONFIG_CINDER_HOST)s",
    internal_address => "%(CONFIG_CINDER_HOST)s",
}

keystone_service { "${cinder::keystone::auth::auth_name}_v2":
    ensure      => present,
    type        => "${cinder::keystone::auth::service_type}v2",
    description => "Cinder Service v2",
}

keystone_endpoint { "${cinder::keystone::auth::region}/${cinder::keystone::auth::auth_name}_v2":
    ensure       => present,
    public_url   => "${cinder::keystone::auth::public_protocol}://${cinder::keystone::auth::public_address}:${cinder::keystone::auth::port}/v2/%%(tenant_id)s",
    admin_url    => "http://${cinder::keystone::auth::admin_address}:${cinder::keystone::auth::port}/v2/%%(tenant_id)s",
    internal_url => "http://${cinder::keystone::auth::internal_address}:${cinder::keystone::auth::port}/v2/%%(tenant_id)s",
}
