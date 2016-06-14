class packstack::neutron ()
{
    $neutron_db_host         = hiera('CONFIG_MARIADB_HOST_URL')
    $neutron_db_name         = hiera('CONFIG_NEUTRON_L2_DBNAME')
    $neutron_db_user         = 'neutron'
    $neutron_db_password     = hiera('CONFIG_NEUTRON_DB_PW')
    $neutron_sql_connection  = "mysql+pymysql://${neutron_db_user}:${neutron_db_password}@${neutron_db_host}/${neutron_db_name}"
    $neutron_user_password   = hiera('CONFIG_NEUTRON_KS_PW')
}
