class packstack::manila::backend::glusternative ()
{
    manila::backend::glusternative{ 'glusternative':
      glusterfs_servers                    => hiera('CONFIG_MANILA_GLUSTERFS_SERVERS'),
      glusterfs_native_path_to_private_key => hiera('CONFIG_MANILA_GLUSTERFS_NATIVE_PATH_TO_PRIVATE_KEY'),
      glusterfs_volume_pattern             => hiera('CONFIG_MANILA_GLUSTERFS_VOLUME_PATTERN'),
    }

    packstack::manila::network{ 'glusternative': }
}
