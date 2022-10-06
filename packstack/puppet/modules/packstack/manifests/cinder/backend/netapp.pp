# Copyright (c) – 2014, Ryan Hefner.  All rights reserved.
class packstack::cinder::backend::netapp ()
{
    $netapp_storage_family = lookup('CONFIG_CINDER_NETAPP_STORAGE_FAMILY')
    $netapp_storage_protocol = lookup('CONFIG_CINDER_NETAPP_STORAGE_PROTOCOL')
    $netapp_backend_name = 'netapp'

    if $netapp_storage_family == 'ontap_cluster' {
      if $netapp_storage_protocol == 'nfs' {
        cinder::backend::netapp { $netapp_backend_name:
          netapp_login              => lookup('CONFIG_CINDER_NETAPP_LOGIN'),
          netapp_password           => lookup('CONFIG_CINDER_NETAPP_PASSWORD'),
          netapp_server_hostname    => lookup('CONFIG_CINDER_NETAPP_HOSTNAME'),
          netapp_server_port        => lookup('CONFIG_CINDER_NETAPP_SERVER_PORT'),
          netapp_storage_family     => lookup('CONFIG_CINDER_NETAPP_STORAGE_FAMILY'),
          netapp_storage_protocol   => lookup('CONFIG_CINDER_NETAPP_STORAGE_PROTOCOL'),
          netapp_transport_type     => lookup('CONFIG_CINDER_NETAPP_TRANSPORT_TYPE'),
          netapp_vserver            => lookup('CONFIG_CINDER_NETAPP_VSERVER'),
          expiry_thres_minutes      => lookup('CONFIG_CINDER_NETAPP_EXPIRY_THRES_MINUTES'),
          thres_avl_size_perc_start => lookup('CONFIG_CINDER_NETAPP_THRES_AVL_SIZE_PERC_START'),
          thres_avl_size_perc_stop  => lookup('CONFIG_CINDER_NETAPP_THRES_AVL_SIZE_PERC_STOP'),
          nfs_shares                => lookup('CONFIG_CINDER_NETAPP_NFS_SHARES', { merge => 'unique' }),
          nfs_shares_config         => lookup('CONFIG_CINDER_NETAPP_NFS_SHARES_CONFIG'),
        }
        ensure_packages(['nfs-utils'], {'ensure' => 'present'})
      }
      elsif $netapp_storage_protocol == 'iscsi' {
        cinder::backend::netapp { $netapp_backend_name:
          netapp_login            => lookup('CONFIG_CINDER_NETAPP_LOGIN'),
          netapp_password         => lookup('CONFIG_CINDER_NETAPP_PASSWORD'),
          netapp_server_hostname  => lookup('CONFIG_CINDER_NETAPP_HOSTNAME'),
          netapp_server_port      => lookup('CONFIG_CINDER_NETAPP_SERVER_PORT'),
          netapp_size_multiplier  => lookup('CONFIG_CINDER_NETAPP_SIZE_MULTIPLIER'),
          netapp_storage_family   => lookup('CONFIG_CINDER_NETAPP_STORAGE_FAMILY'),
          netapp_storage_protocol => lookup('CONFIG_CINDER_NETAPP_STORAGE_PROTOCOL'),
          netapp_transport_type   => lookup('CONFIG_CINDER_NETAPP_TRANSPORT_TYPE'),
          netapp_vserver          => lookup('CONFIG_CINDER_NETAPP_VSERVER'),
        }

        ensure_packages(['iscsi-initiator-utils'], {'ensure' => 'present'})
      }

      elsif $netapp_storage_protocol == 'fc' {
        cinder::backend::netapp { $netapp_backend_name:
          netapp_login            => lookup('CONFIG_CINDER_NETAPP_LOGIN'),
          netapp_password         => lookup('CONFIG_CINDER_NETAPP_PASSWORD'),
          netapp_server_hostname  => lookup('CONFIG_CINDER_NETAPP_HOSTNAME'),
          netapp_server_port      => lookup('CONFIG_CINDER_NETAPP_SERVER_PORT'),
          netapp_size_multiplier  => lookup('CONFIG_CINDER_NETAPP_SIZE_MULTIPLIER'),
          netapp_storage_family   => lookup('CONFIG_CINDER_NETAPP_STORAGE_FAMILY'),
          netapp_storage_protocol => lookup('CONFIG_CINDER_NETAPP_STORAGE_PROTOCOL'),
          netapp_transport_type   => lookup('CONFIG_CINDER_NETAPP_TRANSPORT_TYPE'),
          netapp_vserver          => lookup('CONFIG_CINDER_NETAPP_VSERVER'),
        }
      }
    }
    elsif $netapp_storage_family == 'ontap_7mode' {
      if $netapp_storage_protocol == 'nfs' {
        cinder::backend::netapp { $netapp_backend_name:
          netapp_login              => lookup('CONFIG_CINDER_NETAPP_LOGIN'),
          netapp_password           => lookup('CONFIG_CINDER_NETAPP_PASSWORD'),
          netapp_server_hostname    => lookup('CONFIG_CINDER_NETAPP_HOSTNAME'),
          netapp_server_port        => lookup('CONFIG_CINDER_NETAPP_SERVER_PORT'),
          netapp_storage_family     => lookup('CONFIG_CINDER_NETAPP_STORAGE_FAMILY'),
          netapp_storage_protocol   => lookup('CONFIG_CINDER_NETAPP_STORAGE_PROTOCOL'),
          netapp_transport_type     => lookup('CONFIG_CINDER_NETAPP_TRANSPORT_TYPE'),
          expiry_thres_minutes      => lookup('CONFIG_CINDER_NETAPP_EXPIRY_THRES_MINUTES'),
          thres_avl_size_perc_start => lookup('CONFIG_CINDER_NETAPP_THRES_AVL_SIZE_PERC_START'),
          thres_avl_size_perc_stop  => lookup('CONFIG_CINDER_NETAPP_THRES_AVL_SIZE_PERC_STOP'),
          nfs_shares                => lookup('CONFIG_CINDER_NETAPP_NFS_SHARES', { merge => 'unique' }),
          nfs_shares_config         => lookup('CONFIG_CINDER_NETAPP_NFS_SHARES_CONFIG'),
        }

        ensure_packages(['nfs-utils'], {'ensure' => 'present'})
      }
      elsif $netapp_storage_protocol == 'iscsi' {
        cinder::backend::netapp { $netapp_backend_name:
          netapp_login            => lookup('CONFIG_CINDER_NETAPP_LOGIN'),
          netapp_password         => lookup('CONFIG_CINDER_NETAPP_PASSWORD'),
          netapp_server_hostname  => lookup('CONFIG_CINDER_NETAPP_HOSTNAME'),
          netapp_server_port      => lookup('CONFIG_CINDER_NETAPP_SERVER_PORT'),
          netapp_size_multiplier  => lookup('CONFIG_CINDER_NETAPP_SIZE_MULTIPLIER'),
          netapp_storage_family   => lookup('CONFIG_CINDER_NETAPP_STORAGE_FAMILY'),
          netapp_storage_protocol => lookup('CONFIG_CINDER_NETAPP_STORAGE_PROTOCOL'),
          netapp_transport_type   => lookup('CONFIG_CINDER_NETAPP_TRANSPORT_TYPE'),
          netapp_vfiler           => lookup('CONFIG_CINDER_NETAPP_VFILER'),
          netapp_volume_list      => lookup('CONFIG_CINDER_NETAPP_VOLUME_LIST'),
        }

        ensure_packages(['iscsi-initiator-utils'], {'ensure' => 'present'})
      }

      elsif $netapp_storage_protocol == 'fc' {
        cinder::backend::netapp { $netapp_backend_name:
          netapp_login                => lookup('CONFIG_CINDER_NETAPP_LOGIN'),
          netapp_password             => lookup('CONFIG_CINDER_NETAPP_PASSWORD'),
          netapp_server_hostname      => lookup('CONFIG_CINDER_NETAPP_HOSTNAME'),
          netapp_server_port          => lookup('CONFIG_CINDER_NETAPP_SERVER_PORT'),
          netapp_size_multiplier      => lookup('CONFIG_CINDER_NETAPP_SIZE_MULTIPLIER'),
          netapp_storage_family       => lookup('CONFIG_CINDER_NETAPP_STORAGE_FAMILY'),
          netapp_storage_protocol     => lookup('CONFIG_CINDER_NETAPP_STORAGE_PROTOCOL'),
          netapp_transport_type       => lookup('CONFIG_CINDER_NETAPP_TRANSPORT_TYPE'),
          netapp_vfiler               => lookup('CONFIG_CINDER_NETAPP_VFILER'),
          netapp_partner_backend_name => lookup('CONFIG_CINDER_NETAPP_PARTNER_BACKEND_NAME'),
          netapp_volume_list          => lookup('CONFIG_CINDER_NETAPP_VOLUME_LIST'),
        }
      }
    }
    elsif $netapp_storage_family == 'eseries' {
      cinder::backend::netapp { $netapp_backend_name:
        netapp_login             => lookup('CONFIG_CINDER_NETAPP_LOGIN'),
        netapp_password          => lookup('CONFIG_CINDER_NETAPP_PASSWORD'),
        netapp_server_hostname   => lookup('CONFIG_CINDER_NETAPP_HOSTNAME'),
        netapp_server_port       => lookup('CONFIG_CINDER_NETAPP_SERVER_PORT'),
        netapp_storage_family    => lookup('CONFIG_CINDER_NETAPP_STORAGE_FAMILY'),
        netapp_storage_protocol  => lookup('CONFIG_CINDER_NETAPP_STORAGE_PROTOCOL'),
        netapp_transport_type    => lookup('CONFIG_CINDER_NETAPP_TRANSPORT_TYPE'),
        netapp_controller_ips    => lookup('CONFIG_CINDER_NETAPP_CONTROLLER_IPS'),
        netapp_sa_password       => lookup('CONFIG_CINDER_NETAPP_SA_PASSWORD'),
        netapp_storage_pools     => lookup('CONFIG_CINDER_NETAPP_STORAGE_POOLS'),
        netapp_eseries_host_type => lookup('CONFIG_CINDER_NETAPP_ESERIES_HOST_TYPE'),
        netapp_webservice_path   => lookup('CONFIG_CINDER_NETAPP_WEBSERVICE_PATH'),
      }

        ensure_packages(['iscsi-initiator-utils'], {'ensure' => 'present'})
    }

    cinder_type { $netapp_backend_name:
      ensure     => present,
      properties => ["volume_backend_name=${netapp_backend_name}"],
      require    => Class['cinder::api'],
    }
}
