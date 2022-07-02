class packstack::neutron::ovn_metadata ()
{
    $ovn_southd = "tcp:${lookup('CONFIG_CONTROLLER_HOST')}:6642"

    class { 'neutron::agents::ovn_metadata':
      ovn_sb_connection => $ovn_southd,
      shared_secret     => lookup('CONFIG_NEUTRON_METADATA_PW'),
      metadata_host     => force_ip(lookup('CONFIG_KEYSTONE_HOST_URL')),
      debug             => lookup('CONFIG_DEBUG_MODE'),
      metadata_workers  => lookup('CONFIG_SERVICE_WORKERS'),
    }
    Service<| title == 'controller' |> -> Service<| title == 'ovn-metadata' |>
}
