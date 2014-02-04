
class {'cinder':
    rpc_backend    => 'cinder.openstack.common.rpc.impl_qpid',
    qpid_hostname  => "%(CONFIG_QPID_HOST)s",
    qpid_port      => '%(CONFIG_QPID_CLIENTS_PORT)s',
    qpid_protocol  => '%(CONFIG_QPID_PROTOCOL)s',
    qpid_username  => '%(CONFIG_QPID_AUTH_USER)s',
    qpid_password  => '%(CONFIG_QPID_AUTH_PASSWORD)s',
    sql_connection => "mysql://cinder:%(CONFIG_CINDER_DB_PW)s@%(CONFIG_MYSQL_HOST)s/cinder",
    verbose        => true,
    debug          => %(CONFIG_DEBUG_MODE)s,
}

cinder_config {
    "DEFAULT/glance_host": value => "%(CONFIG_GLANCE_HOST)s";
}

package {'python-keystone':
    notify => Class['cinder::api'],
}

class {'cinder::api':
    keystone_password => '%(CONFIG_CINDER_KS_PW)s',
    keystone_tenant => "services",
    keystone_user => "cinder",
    keystone_auth_host => "%(CONFIG_KEYSTONE_HOST)s",
}

class {'cinder::scheduler':
}

class {'cinder::volume':
}

class {'cinder::volume::iscsi':
    iscsi_ip_address => '%(CONFIG_CINDER_HOST)s'
}
