class packstack::neutron ()
{
    $neutron_db_host         = lookup('CONFIG_MARIADB_HOST_URL')
    $neutron_db_name         = lookup('CONFIG_NEUTRON_L2_DBNAME')
    $neutron_db_user         = 'neutron'
    $neutron_db_password     = lookup('CONFIG_NEUTRON_DB_PW')
    $neutron_sql_connection  = "mysql+pymysql://${neutron_db_user}:${neutron_db_password}@${neutron_db_host}/${neutron_db_name}"
    $neutron_user_password   = lookup('CONFIG_NEUTRON_KS_PW')
}
