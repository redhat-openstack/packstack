stage { "init": before  => Stage["main"] }

Exec { timeout => lookup('DEFAULT_EXEC_TIMEOUT') }
Package { allow_virtual => true }

class { 'packstack::prereqs':
  stage => init,
}

include nova::cell_v2::discover_hosts

notify {'Discovering compute nodes': } ~> Class['nova::cell_v2::discover_hosts']


