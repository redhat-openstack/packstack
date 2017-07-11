class packstack::openstackclient ()
{
    $clientlibs = ['python-novaclient',
      'python-glanceclient',
      'python-cinderclient', 'python-openstackclient']

    ensure_packages($clientlibs, {'ensure' => 'present'})

    if hiera('CONFIG_MANILA_INSTALL') == 'y' {
      ensure_packages(['python-manilaclient'], {'ensure' => 'present'})
    }

    $ost_cl_keystone_admin_username = hiera('CONFIG_KEYSTONE_ADMIN_USERNAME')
    $ost_cl_keystone_admin_pw       = hiera('CONFIG_KEYSTONE_ADMIN_PW')
    $ost_cl_ctrl_keystone_url       = hiera('CONFIG_KEYSTONE_PUBLIC_URL')
    $ost_cl_keystone_region         = hiera('CONFIG_KEYSTONE_REGION')
    $ost_cl_keystone_demo_pw        = hiera('CONFIG_KEYSTONE_DEMO_PW')

    $config_keystone_api_version = hiera('CONFIG_KEYSTONE_API_VERSION')
    if $config_keystone_api_version =~ /^v(\d+).*$/ {
      # we need to force integer here
      $int_api_version = 0 + $1
    } else {
      fail("${config_keystone_api_version} is an incorrect Keystone API Version!")
    }

    $rcadmin_common_content = "unset OS_SERVICE_TOKEN
    export OS_USERNAME=${ost_cl_keystone_admin_username}
    export OS_PASSWORD='${ost_cl_keystone_admin_pw}'
    export OS_AUTH_URL=${ost_cl_ctrl_keystone_url}
    export PS1='[\\u@\\h \\W(keystone_admin)]\\$ '
    "

    if $int_api_version < 3 {
      $rcadmin_content = "${rcadmin_common_content}
export OS_TENANT_NAME=admin
export OS_REGION_NAME=${ost_cl_keystone_region}
    "
    }
    else {
        $rcadmin_content = "${rcadmin_common_content}
export OS_PROJECT_NAME=admin
export OS_USER_DOMAIN_NAME=Default
export OS_PROJECT_DOMAIN_NAME=Default
export OS_IDENTITY_API_VERSION=${int_api_version}
    "
    }

    file { "${::home_dir}/keystonerc_admin":
      ensure  => file,
      mode    => '0600',
      content => $rcadmin_content,
    }

    if hiera('CONFIG_PROVISION_DEMO') == 'y' {
      $demo_common_content = "unset OS_SERVICE_TOKEN
export OS_USERNAME=demo
export OS_PASSWORD='${ost_cl_keystone_demo_pw}'
export PS1='[\\u@\\h \\W(keystone_demo)]\\$ '
export OS_AUTH_URL=${ost_cl_ctrl_keystone_url}
    "

      if $int_api_version < 3 {
        $demo_content = "${demo_common_content}
export OS_TENANT_NAME=demo
export OS_IDENTITY_API_VERSION=${int_api_version}.0
    "
      } else {
        $demo_content = "${demo_common_content}
export OS_PROJECT_NAME=demo
export OS_USER_DOMAIN_NAME=Default
export OS_PROJECT_DOMAIN_NAME=Default
export OS_IDENTITY_API_VERSION=${int_api_version}
    "
      }

      file { "${::home_dir}/keystonerc_demo":
        ensure  => file,
        mode    => '0600',
        content => $demo_content,
      }
    }

    if hiera('NO_ROOT_USER_ALLINONE') == true {
      $ost_cl_home_dir = hiera('HOME_DIR')
      file { "${ost_cl_home_dir}/keystonerc_admin":
        ensure  => file,
        owner   => hiera('NO_ROOT_USER'),
        group   => hiera('NO_ROOT_GROUP'),
        mode    => '0600',
        content => $rcadmin_content,
      }
    }
}
