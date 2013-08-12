
require 'keystone::python'
class {"nova::api":
    enabled => true,
    auth_host => "%(CONFIG_KEYSTONE_HOST)s",
    admin_password => "%(CONFIG_NOVA_KS_PW)s",
    neutron_metadata_proxy_shared_secret => %(CONFIG_NEUTRON_METADATA_PW_UNQUOTED)s
}

Package<| title == 'nova-common' |> -> Class['nova::api']

firewall { '001 novaapi incoming':
    proto    => 'tcp',
    dport    => ['8773', '8774', '8775'],
    action   => 'accept',
}
