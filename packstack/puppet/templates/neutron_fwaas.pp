class { 'neutron::services::fwaas':
  enabled => true,
}

Class['neutron::services::fwaas'] -> Class['neutron::agents::l3']
