class { 'cinder::backup': }

$cinder_backup_conf_ctrl_host = hiera('CONFIG_CONTROLLER_HOST')

class { 'cinder::backup::swift':
  backup_swift_url => "http://${cinder_config_controller_host}:8080/v1/AUTH_",
}

Class['cinder::api'] ~> Service['cinder-backup']


