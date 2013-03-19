
package {"clientdeps":
    name => ["python-iso8601"]
}

package {"clientlibs":
    name => ["python-novaclient", "python-keystoneclient", "python-glanceclient", "python-swiftclient", "python-cinderclient"]
}

file {"${::home_dir}/keystonerc_admin":
   ensure  => "present",
   mode => '0600',
   content => "export OS_USERNAME=admin
export OS_TENANT_NAME=admin
export OS_PASSWORD=%(CONFIG_KEYSTONE_ADMIN_PW)s
export OS_AUTH_URL=http://%(CONFIG_KEYSTONE_HOST)s:35357/v2.0/
export PS1='[\\u@\\h \\W(keystone_admin)]\\$ '
",
}
