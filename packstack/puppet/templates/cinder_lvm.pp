$create_cinder_volume = hiera('CONFIG_CINDER_VOLUMES_CREATE')

if $create_cinder_volume == 'y' {
    class { '::cinder::setup_test_volume':
      size            => hiera('CONFIG_CINDER_VOLUMES_SIZE'),
      loopback_device => '/dev/loop2',
      volume_path     => '/var/lib/cinder',
      volume_name     => 'cinder-volumes',
    }

    # Add loop device on boot
    $el_releases = ['RedHat', 'CentOS', 'Scientific']
    if $::operatingsystem in $el_releases and (versioncmp($::operatingsystemmajrelease, '7') < 0) {

      file_line{ 'rc.local_losetup_cinder_volume':
        path  => '/etc/rc.d/rc.local',
        match => '^.*/var/lib/cinder/cinder-volumes.*$',
        line  => 'losetup -f /var/lib/cinder/cinder-volumes && service openstack-cinder-volume restart',
      }

      file { '/etc/rc.d/rc.local':
        mode  => '0755',
      }

    } else {

      file { 'openstack-losetup':
        path    => '/usr/lib/systemd/system/openstack-losetup.service',
        before  => Service['openstack-losetup'],
        notify  => Exec['/usr/bin/systemctl daemon-reload'],
        content => '[Unit]
Description=Setup cinder-volume loop device
DefaultDependencies=false
Before=openstack-cinder-volume.service
After=local-fs.target

[Service]
Type=oneshot
ExecStart=/usr/bin/sh -c \'/usr/sbin/losetup -j /var/lib/cinder/cinder-volumes | /usr/bin/grep /var/lib/cinder/cinder-volumes || /usr/sbin/losetup -f /var/lib/cinder/cinder-volumes\'
ExecStop=/usr/bin/sh -c \'/usr/sbin/losetup -j /var/lib/cinder/cinder-volumes | /usr/bin/cut -d : -f 1 | /usr/bin/xargs /usr/sbin/losetup -d\'
TimeoutSec=60
RemainAfterExit=yes

[Install]
RequiredBy=openstack-cinder-volume.service',
      }

      exec { '/usr/bin/systemctl daemon-reload':
        refreshonly => true,
        before      => Service['openstack-losetup'],
      }

      service { 'openstack-losetup':
        ensure  => running,
        enable  => true,
        require => Class['cinder::setup_test_volume'],
      }

    }
}
else {
    package {'lvm2':
      ensure => 'present',
    }
}


file_line { 'snapshot_autoextend_threshold':
  path    => '/etc/lvm/lvm.conf',
  match   => '^\s*snapshot_autoextend_threshold +=.*',
  line    => '   snapshot_autoextend_threshold = 80',
  require => Package['lvm2'],
}

file_line { 'snapshot_autoextend_percent':
  path    => '/etc/lvm/lvm.conf',
  match   => '^\s*snapshot_autoextend_percent +=.*',
  line    => '   snapshot_autoextend_percent = 20',
  require => Package['lvm2'],
}

cinder::backend::iscsi { 'lvm':
  iscsi_ip_address => hiera('CONFIG_STORAGE_HOST_URL'),
  require          => Package['lvm2'],
}

cinder::type { 'iscsi':
  set_key   => 'volume_backend_name',
  set_value => 'lvm',
  require   => Class['cinder::api'],
}
