
class {'horizon':
   secret_key => '%(DASHBOARD_SECRET_KEY)s',
   keystone_host => '%(CONFIG_KEYSTONE_HOST)s',
}

class {'memcached':}
