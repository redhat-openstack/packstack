class packstack::nova::metadata ()
{
    nova::generic_service { 'metadata-api':
        enabled        => true,
        ensure_package => 'present',
        package_name   => 'openstack-nova-api',
        service_name   => 'openstack-nova-metadata-api',
    }
}
