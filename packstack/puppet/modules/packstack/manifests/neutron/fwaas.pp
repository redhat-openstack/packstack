class packstack::neutron::fwaas ()
{
    class { '::neutron::services::fwaas':
      enabled => true,
      agent_version => 'v2',
      driver  => 'neutron_fwaas.services.firewall.service_drivers.agents.drivers.linux.iptables_fwaas_v2.IptablesFwaasDriver',
    }
}
