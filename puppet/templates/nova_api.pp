
require 'keystone::python'
class {"nova::api":
    enabled => true,
    auth_host => "%(CONFIG_KEYSTONE_HOST)s",
    admin_password => "nova_default_password",
}

firewall { '001 novaapi incomming':
    proto    => 'tcp',
    dport    => ['8773', '8774', '8776'],
    action   => 'accept',
}
