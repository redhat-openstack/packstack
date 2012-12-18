
require 'keystone::python'
class {"nova::api":
    enabled => true,
    auth_host => "%(CONFIG_KEYSTONE_HOST)s",
    admin_password => "nova_default_password",
}

Package<| title == 'nova-common' |> -> Class['nova::api']

firewall { '001 novaapi incoming':
    proto    => 'tcp',
    dport    => ['8773', '8774'],
    action   => 'accept',
}
