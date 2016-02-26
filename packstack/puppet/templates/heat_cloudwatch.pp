
class { '::heat::api_cloudwatch':
  workers => $service_workers
}

