if hiera('CONFIG_HORIZON_SSL')  == 'y' {
  apache::listen { '443': }
}

if hiera('CONFIG_KEYSTONE_SERVICE_NAME') == 'httpd' {
  apache::listen { '5000': }
  apache::listen { '35357': }
}

if hiera('CONFIG_CEILOMETER_INSTALL') == 'y' {
  if hiera('CONFIG_CEILOMETER_SERVICE_NAME') == 'httpd' {
    apache::listen { '8777': }
  }
}

if hiera('CONFIG_AODH_INSTALL') == 'y' {
  apache::listen { '8042': }
}

if hiera('CONFIG_GNOCCHI_INSTALL') == 'y' {
  apache::listen { '8041': }
}

