class packstack::nova::nfs ()
{
 ensure_packages(['nfs-utils'], {'ensure' => 'present'})
}
