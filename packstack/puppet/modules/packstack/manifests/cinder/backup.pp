class packstack::cinder::backup ()
{
    class { 'cinder::backup': }

    $cinder_backup_conf_ctrl_host = lookup('CONFIG_KEYSTONE_HOST_URL')

    class { 'cinder::backup::swift':
      backup_swift_url          => "http://${cinder_backup_conf_ctrl_host}:8080/v1/AUTH_",
      backup_swift_service_auth => true
    }

    Class['cinder::api'] ~> Service['cinder-backup']
}
