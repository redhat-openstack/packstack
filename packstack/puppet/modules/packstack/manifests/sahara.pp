class packstack::sahara ()
{
    create_resources(packstack::firewall, hiera('FIREWALL_SAHARA_CFN_RULES', {}))

    class { '::sahara::service::api':
      api_workers => hiera('CONFIG_SERVICE_WORKERS')
    }

    class { '::sahara::service::engine': }
}
