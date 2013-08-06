$neutron_db_host = '%(CONFIG_MYSQL_HOST)s'
$neutron_db_name = '%(CONFIG_NEUTRON_L2_DBNAME)s'
$neutron_db_user = 'neutron'
$neutron_db_password = '%(CONFIG_NEUTRON_DB_PW)s'
$neutron_sql_connection = "mysql://${neutron_db_user}:${neutron_db_password}@${neutron_db_host}/${neutron_db_name}"

$neutron_user_password = '%(CONFIG_NEUTRON_KS_PW)s'

class { 'neutron':
  rpc_backend => 'neutron.openstack.common.rpc.impl_qpid',
  qpid_hostname => '%(CONFIG_QPID_HOST)s',
  core_plugin => '%(CONFIG_NEUTRON_CORE_PLUGIN)s',
  verbose => true,
}
