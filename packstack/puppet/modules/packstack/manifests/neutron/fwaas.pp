class packstack::neutron::fwaas ()
{
    class { '::neutron::services::fwaas':
      enabled => true,
      agent_version => 'v1',
      driver  => 'neutron_fwaas.services.firewall.drivers.linux.iptables_fwaas.IptablesFwaasDriver',
    }
}
