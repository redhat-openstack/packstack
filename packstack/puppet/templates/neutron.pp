$neutron_db_host = '%(CONFIG_MARIADB_HOST)s'
$neutron_db_name = '%(CONFIG_NEUTRON_L2_DBNAME)s'
$neutron_db_user = 'neutron'
$neutron_db_password = '%(CONFIG_NEUTRON_DB_PW)s'
$neutron_sql_connection = "mysql://${neutron_db_user}:${neutron_db_password}@${neutron_db_host}/${neutron_db_name}"

$neutron_user_password = '%(CONFIG_NEUTRON_KS_PW)s'


