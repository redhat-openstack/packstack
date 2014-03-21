class {"heat::db":
    sql_connection => "mysql://heat:%(CONFIG_HEAT_DB_PW)s@%(CONFIG_MYSQL_HOST)s/heat"
}

class { 'heat::api_cloudwatch':
}
