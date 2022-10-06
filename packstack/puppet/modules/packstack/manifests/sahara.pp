class packstack::sahara ()
{
    create_resources(packstack::firewall, lookup('FIREWALL_SAHARA_CFN_RULES', undef, undef, {}))

    class { 'sahara::service::api':
      api_workers => lookup('CONFIG_SERVICE_WORKERS')
    }

    class { 'sahara::service::engine': }
}
