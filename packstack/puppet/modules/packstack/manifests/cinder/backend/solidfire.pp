# Copyright (c) – 2016, Edward Balduf. All rights reserved.
class packstack::cinder::backend::solidfire ()
{
    $solidfire_backend_name = 'solidfire'

    cinder::backend::solidfire { $solidfire_backend_name :
        san_ip               => hiera('CONFIG_CINDER_SOLIDFIRE_LOGIN'),
        san_login            => hiera('CONFIG_CINDER_SOLIDFIRE_PASSWORD'),
        san_password         => hiera('CONFIG_CINDER_SOLIDFIRE_HOSTNAME'),
        volume_backend_name  => $solidfire_backend_name,
    }

    ensure_packages(['iscsi-initiator-utils'], {'ensure' => 'present'})

    cinder::type { $solidfire_backend_name:
      set_key   => 'volume_backend_name',
      set_value => $solidfire_backend_name,
      require   => Class['cinder::api'],
    }
}
