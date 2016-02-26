class { '::sahara::service::api':
  api_workers => $service_workers
}

class { '::sahara::service::engine': }
