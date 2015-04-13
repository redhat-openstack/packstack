
$clientdeps = ['python-iso8601']
package { $clientdeps: }

$clientlibs = ['python-novaclient', 'python-keystoneclient',
  'python-glanceclient', 'python-swiftclient',
  'python-cinderclient', 'python-openstackclient']

package { $clientlibs: }

$ost_cl_keystone_admin_username = hiera('CONFIG_KEYSTONE_ADMIN_USERNAME')
$ost_cl_keystone_admin_pw       = hiera('CONFIG_KEYSTONE_ADMIN_PW')
$ost_cl_ctrl_host               = hiera('CONFIG_CONTROLLER_HOST')
$ost_cl_keystone_region         = hiera('CONFIG_KEYSTONE_REGION')
$ost_cl_keystone_demo_pw        = hiera('CONFIG_KEYSTONE_DEMO_PW')
$rcadmin_content = "export OS_USERNAME=${ost_cl_keystone_admin_username}
export OS_TENANT_NAME=admin
export OS_PASSWORD=${ost_cl_keystone_admin_pw}
export OS_AUTH_URL=http://${ost_cl_ctrl_host}:5000/v2.0/
export OS_REGION_NAME=${ost_cl_keystone_region}
export PS1='[\\u@\\h \\W(keystone_admin)]\\$ '
"

file { "${::home_dir}/keystonerc_admin":
  ensure  => 'present',
  mode    => '0600',
  content => $rcadmin_content,
}

if hiera('CONFIG_PROVISION_DEMO') == 'y' {
  file { "${::home_dir}/keystonerc_demo":
    ensure  => 'present',
    mode    => '0600',
    content => "export OS_USERNAME=demo
export OS_TENANT_NAME=demo
export OS_PASSWORD=${ost_cl_keystone_demo_pw}
export OS_AUTH_URL=http://${ost_cl_ctrl_host}:5000/v2.0/
export PS1='[\\u@\\h \\W(keystone_demo)]\\$ '
",
  }
}

if hiera('NO_ROOT_USER_ALLINONE') == true {
  $ost_cl_home_dir = hiera('HOME_DIR')
  file { "${ost_cl_home_dir}/keystonerc_admin":
    ensure  => present,
    owner   => hiera('NO_ROOT_USER'),
    group   => hiera('NO_ROOT_GROUP'),
    mode    => '0600',
    content => $rcadmin_content,
  }
}
