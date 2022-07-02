class packstack::manila::backend::glusternative ()
{
    manila::backend::glusternative{ 'glusternative':
      glusterfs_servers                    => lookup('CONFIG_MANILA_GLUSTERFS_SERVERS'),
      glusterfs_path_to_private_key        => lookup('CONFIG_MANILA_GLUSTERFS_NATIVE_PATH_TO_PRIVATE_KEY'),
      glusterfs_volume_pattern             => lookup('CONFIG_MANILA_GLUSTERFS_VOLUME_PATTERN'),
    }

    packstack::manila::network{ 'glusternative': }
}
