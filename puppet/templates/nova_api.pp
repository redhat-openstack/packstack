
require 'keystone::python'
class {"nova::api":
    enabled => true,
    auth_host => "%(CONFIG_KEYSTONE_HOST)s",
    admin_password => "nova_password",
}

# the notify in the nova:api class doesn't work, so need to set these ones
# TODO : figure this out
Package<| title == 'nova-common' |> ~> Exec['initial-db-sync']
Package<| title == 'nova-common' |> ~> File['/etc/nova/api-paste.ini']


firewall { '001 novaapi incomming':
    proto    => 'tcp',
    dport    => ['8773', '8774', '8776'],
    action   => 'accept',
}
