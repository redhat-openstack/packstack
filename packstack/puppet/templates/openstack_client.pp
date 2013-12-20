
$clientdeps = ["python-iso8601"]
package { $clientdeps: }

$clientlibs = ["python-novaclient", "python-keystoneclient", "python-glanceclient", "python-swiftclient", "python-cinderclient"]
package { $clientlibs: }

$rcadmin_content = "export OS_USERNAME=admin
export OS_TENANT_NAME=admin
export OS_PASSWORD=%(CONFIG_KEYSTONE_ADMIN_PW)s
export OS_AUTH_URL=http://%(CONFIG_KEYSTONE_HOST)s:35357/v2.0/
export PS1='[\\u@\\h \\W(keystone_admin)]\\$ '
"

file {"${::home_dir}/keystonerc_admin":
   ensure  => "present",
   mode => '0600',
   content => $rcadmin_content,
}

if '%(CONFIG_PROVISION_DEMO)s' == 'y' {
   file {"${::home_dir}/keystonerc_demo":
      ensure  => "present",
      mode => '0600',
      content => "export OS_USERNAME=demo
export OS_TENANT_NAME=demo
export OS_PASSWORD=%(CONFIG_KEYSTONE_DEMO_PW)s
export OS_AUTH_URL=http://%(CONFIG_KEYSTONE_HOST)s:35357/v2.0/
export PS1='[\\u@\\h \\W(keystone_demo)]\\$ '
",
   }
}

if %(NO_ROOT_USER_ALLINONE)s {
    file {"%(HOME_DIR)s/keystonerc_admin":
       ensure => present,
       owner => '%(NO_ROOT_USER)s',
       group => '%(NO_ROOT_GROUP)s',
       mode => '0600',
       content => $rcadmin_content,
    }
}
