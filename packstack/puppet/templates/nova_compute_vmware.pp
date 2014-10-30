class { 'nova::compute::vmware':
  host_ip       => hiera('CONFIG_VCENTER_HOST'),
  host_username => hiera('CONFIG_VCENTER_USER'),
  host_password => hiera('CONFIG_VCENTER_PASSWORD'),
  cluster_name  => hiera('CONFIG_VCENTER_CLUSTER_NAME'),
}
