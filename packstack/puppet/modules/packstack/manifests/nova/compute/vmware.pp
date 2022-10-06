class packstack::nova::compute::vmware ()
{
    $cluster_list = lookup('CONFIG_VCENTER_CLUSTERS')
    $my_ip = choose_my_ip(lookup('HOST_LIST'))
    $nova_vcenter_cluster_name = $cluster_list[$my_ip]

    class { 'nova::compute::vmware':
      host_ip       => lookup('CONFIG_VCENTER_HOST'),
      host_username => lookup('CONFIG_VCENTER_USER'),
      host_password => lookup('CONFIG_VCENTER_PASSWORD'),
      cluster_name  => $nova_vcenter_cluster_name,
    }
}
