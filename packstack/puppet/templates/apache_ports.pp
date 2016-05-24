if hiera('CONFIG_HORIZON_SSL')  == 'y' {
  apache::listen { '443': }
}

if hiera('CONFIG_KEYSTONE_SERVICE_NAME') == 'httpd' {
  apache::listen { '5000': }
  apache::listen { '35357': }
}

