class packstack::neutron::ovn_metadata ()
{
    $ovn_southd = "tcp:${hiera('CONFIG_CONTROLLER_HOST')}:6642"

    class { '::neutron::agents::ovn_metadata':
      ovn_sb_connection => $ovn_southd,
      shared_secret    => hiera('CONFIG_NEUTRON_METADATA_PW'),
      metadata_ip      => force_ip(hiera('CONFIG_KEYSTONE_HOST_URL')),
      debug            => hiera('CONFIG_DEBUG_MODE'),
      metadata_workers => hiera('CONFIG_SERVICE_WORKERS'),
    }
    Service<| title == 'controller' |> -> Service<| title == 'ovn-metadata' |>
}
