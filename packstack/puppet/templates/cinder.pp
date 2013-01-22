
class {'cinder::base':
    rabbit_password => '',
    sql_connection => "mysql://cinder:%(CONFIG_CINDER_DB_PW)s@%(CONFIG_MYSQL_HOST)s/cinder"
}

cinder_config{
    "DEFAULT/rpc_backend": value => "cinder.openstack.common.rpc.impl_qpid";
    "DEFAULT/qpid_hostname": value => "%(CONFIG_QPID_HOST)s";
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

firewall { '001 cinder incoming':
    proto    => 'tcp',
    dport    => ['3260', '8776'],
    action   => 'accept',
}
