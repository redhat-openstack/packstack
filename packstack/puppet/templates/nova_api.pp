
require 'keystone::python'
class {"nova::api":
    enabled => true,
    auth_host => "%(CONFIG_KEYSTONE_HOST)s",
    admin_password => "%(CONFIG_NOVA_KS_PW)s",
}

Package<| title == 'nova-common' |> -> Class['nova::api']

firewall { '001 novaapi incoming':
    proto    => 'tcp',
    dport    => ['8773', '8774'],
    action   => 'accept',
}
