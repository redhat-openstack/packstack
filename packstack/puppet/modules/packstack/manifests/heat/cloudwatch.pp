class packstack::heat::cloudwatch ()
{
    create_resources(packstack::firewall, hiera('FIREWALL_HEAT_CLOUDWATCH_RULES', {}))

    class { '::heat::api_cloudwatch':
      workers => hiera('CONFIG_SERVICE_WORKERS'),
    }
}
