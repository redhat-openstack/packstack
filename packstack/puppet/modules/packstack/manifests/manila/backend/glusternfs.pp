class packstack::manila::backend::glusternfs ()
{
    manila::backend::glusternfs{ 'glusternfs':
      glusterfs_target              => lookup('CONFIG_MANILA_GLUSTERFS_TARGET'),
      glusterfs_mount_point_base    => lookup('CONFIG_MANILA_GLUSTERFS_MOUNT_POINT_BASE'),
      glusterfs_nfs_server_type     => lookup('CONFIG_MANILA_GLUSTERFS_NFS_SERVER_TYPE'),
      glusterfs_path_to_private_key => lookup('CONFIG_MANILA_GLUSTERFS_PATH_TO_PRIVATE_KEY'),
      glusterfs_ganesha_server_ip   => lookup('CONFIG_MANILA_GLUSTERFS_GANESHA_SERVER_IP'),
    }

    packstack::manila::network{ 'glusternfs': }

    include  '::manila::ganesha'
}
