class packstack::nova::gluster ()
{
 ensure_packages(['glusterfs-fuse'], {'ensure' => 'present'})
}
