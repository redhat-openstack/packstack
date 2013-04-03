$quantum_db_host     = '%(CONFIG_MYSQL_HOST)s'
$quantum_db_name     = 'quantum'
$quantum_db_user = 'quantum'
$quantum_db_password = '%(CONFIG_QUANTUM_DB_PW)s'
$quantum_sql_connection = "mysql://${quantum_db_user}:${quantum_db_password}@${quantum_db_host}/${quantum_db_name}"

$quantum_user_password = '%(CONFIG_QUANTUM_KS_PW)s'

# set up a quantum server
class { 'quantum':
  rpc_backend => 'quantum.openstack.common.rpc.impl_qpid',
  qpid_hostname => '%(CONFIG_QPID_HOST)s',
}

class { 'quantum::server':
  auth_password => $quantum_user_password,
  auth_host => '%(CONFIG_KEYSTONE_HOST)s',
  enabled => '%(CONFIG_QUANTUM_SERVER_ENABLE)s',
}
