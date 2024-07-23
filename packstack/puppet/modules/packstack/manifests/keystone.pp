class packstack::keystone ()
{
    create_resources(packstack::firewall, lookup('FIREWALL_KEYSTONE_RULES', undef, undef, {}))

    $keystone_use_ssl = false
    $keystone_cfg_ks_db_pw = lookup('CONFIG_KEYSTONE_DB_PW')
    $keystone_cfg_mariadb_host = lookup('CONFIG_MARIADB_HOST_URL')
    $keystone_token_provider_str = downcase(lookup('CONFIG_KEYSTONE_TOKEN_FORMAT'))
    $keystone_url = regsubst(regsubst(lookup('CONFIG_KEYSTONE_PUBLIC_URL'),'/v2.0',''),'/v3','')
    $keystone_admin_url = lookup('CONFIG_KEYSTONE_ADMIN_URL')

    class { 'keystone::client': }

    if lookup('CONFIG_KEYSTONE_FERNET_TOKEN_ROTATE_ENABLE', undef, undef, false) {
      class { 'keystone::cron::fernet_rotate':
        require     => Service['crond'],
      }
      package { 'cronie':
        ensure => 'installed',
        name   => 'cronie',
      }
      service { 'crond':
        ensure  => 'running',
        enable  => true,
        require => Package['cronie'],
      }
    }

    class { 'keystone::logging':
      debug => lookup('CONFIG_DEBUG_MODE'),
    }

    class { 'keystone::db':
      database_connection => "mysql+pymysql://keystone_admin:${keystone_cfg_ks_db_pw}@${keystone_cfg_mariadb_host}/keystone",
    }

    class { 'keystone':
      token_provider      => $keystone_token_provider_str,
      enable_fernet_setup => true,
      service_name        => 'httpd',
      default_domain      => 'Default',
    }

    class { 'keystone::wsgi::apache':
      workers => lookup('CONFIG_SERVICE_WORKERS'),
      ssl     => $keystone_use_ssl
    }

    class { 'keystone::bootstrap':
      password     => lookup('CONFIG_KEYSTONE_ADMIN_PW'),
      username     => lookup('CONFIG_KEYSTONE_ADMIN_USERNAME'),
      email        => lookup('CONFIG_KEYSTONE_ADMIN_EMAIL'),
      project_name => 'admin',
      role_name    => 'admin',
      admin_url    => $keystone_admin_url,
      public_url   => $keystone_url,
      internal_url => $keystone_url,
      region       => lookup('CONFIG_KEYSTONE_REGION'),
    }

    # default assignment driver is SQL
    $assignment_driver = 'keystone.assignment.backends.sql.Assignment'

    if lookup('CONFIG_KEYSTONE_IDENTITY_BACKEND') == 'ldap' {

      if lookup('CONFIG_KEYSTONE_LDAP_USER_ENABLED_EMULATION_DN', undef, undef, undef) {
        $user_enabled_emulation = true
      } else {
        $user_enabled_emulation = false
      }

      class { 'keystone::ldap':
        url                                => lookup('CONFIG_KEYSTONE_LDAP_URL', undef, undef, undef),
        user                               => lookup('CONFIG_KEYSTONE_LDAP_USER_DN', undef, undef, undef),
        password                           => lookup('CONFIG_KEYSTONE_LDAP_USER_PASSWORD', undef, undef, undef),
        suffix                             => lookup('CONFIG_KEYSTONE_LDAP_SUFFIX', undef, undef, undef),
        query_scope                        => lookup('CONFIG_KEYSTONE_LDAP_QUERY_SCOPE', undef, undef, undef),
        page_size                          => lookup('CONFIG_KEYSTONE_LDAP_PAGE_SIZE', undef, undef, undef),
        user_tree_dn                       => lookup('CONFIG_KEYSTONE_LDAP_USER_SUBTREE', undef, undef, undef),
        user_filter                        => lookup('CONFIG_KEYSTONE_LDAP_USER_FILTER', undef, undef, undef),
        user_objectclass                   => lookup('CONFIG_KEYSTONE_LDAP_USER_OBJECTCLASS', undef, undef, undef),
        user_id_attribute                  => lookup('CONFIG_KEYSTONE_LDAP_USER_ID_ATTRIBUTE', undef, undef, undef),
        user_name_attribute                => lookup('CONFIG_KEYSTONE_LDAP_USER_NAME_ATTRIBUTE', undef, undef, undef),
        user_mail_attribute                => lookup('CONFIG_KEYSTONE_LDAP_USER_MAIL_ATTRIBUTE', undef, undef, undef),
        user_enabled_attribute             => lookup('CONFIG_KEYSTONE_LDAP_USER_ENABLED_ATTRIBUTE', undef, undef, undef),
        user_enabled_mask                  => lookup('CONFIG_KEYSTONE_LDAP_USER_ENABLED_MASK', undef, undef, undef),
        user_enabled_default               => lookup('CONFIG_KEYSTONE_LDAP_USER_ENABLED_DEFAULT', undef, undef, undef),
        user_enabled_invert                => lookup('CONFIG_KEYSTONE_LDAP_USER_ENABLED_INVERT', undef, undef, undef),
        user_attribute_ignore              => lookup('CONFIG_KEYSTONE_LDAP_USER_ATTRIBUTE_IGNORE', undef, undef, undef),
        user_default_project_id_attribute  => lookup('CONFIG_KEYSTONE_LDAP_USER_DEFAULT_PROJECT_ID_ATTRIBUTE', undef, undef, undef),
        user_pass_attribute                => lookup('CONFIG_KEYSTONE_LDAP_USER_PASS_ATTRIBUTE', undef, undef, undef),
        user_enabled_emulation             => $user_enabled_emulation,
        user_enabled_emulation_dn          => lookup('CONFIG_KEYSTONE_LDAP_USER_ENABLED_EMULATION_DN', undef, undef, undef),
        user_additional_attribute_mapping  => lookup('CONFIG_KEYSTONE_LDAP_USER_ADDITIONAL_ATTRIBUTE_MAPPING', undef, undef, undef),
        group_tree_dn                      => lookup('CONFIG_KEYSTONE_LDAP_GROUP_SUBTREE', undef, undef, undef),
        group_filter                       => lookup('CONFIG_KEYSTONE_LDAP_GROUP_FILTER', undef, undef, undef),
        group_objectclass                  => lookup('CONFIG_KEYSTONE_LDAP_GROUP_OBJECTCLASS', undef, undef, undef),
        group_id_attribute                 => lookup('CONFIG_KEYSTONE_LDAP_GROUP_ID_ATTRIBUTE', undef, undef, undef),
        group_name_attribute               => lookup('CONFIG_KEYSTONE_LDAP_GROUP_NAME_ATTRIBUTE', undef, undef, undef),
        group_member_attribute             => lookup('CONFIG_KEYSTONE_LDAP_GROUP_MEMBER_ATTRIBUTE', undef, undef, undef),
        group_desc_attribute               => lookup('CONFIG_KEYSTONE_LDAP_GROUP_DESC_ATTRIBUTE', undef, undef, undef),
        group_attribute_ignore             => lookup('CONFIG_KEYSTONE_LDAP_GROUP_ATTRIBUTE_IGNORE', undef, undef, undef),
        group_additional_attribute_mapping => lookup('CONFIG_KEYSTONE_LDAP_GROUP_ADDITIONAL_ATTRIBUTE_MAPPING', undef, undef, undef),
        use_tls                            => lookup('CONFIG_KEYSTONE_LDAP_USE_TLS', undef, undef, undef),
        tls_cacertdir                      => lookup('CONFIG_KEYSTONE_LDAP_TLS_CACERTDIR', undef, undef, undef),
        tls_cacertfile                     => lookup('CONFIG_KEYSTONE_LDAP_TLS_CACERTFILE', undef, undef, undef),
        tls_req_cert                       => lookup('CONFIG_KEYSTONE_LDAP_TLS_REQ_CERT', undef, undef, undef),
        identity_driver                    => 'keystone.identity.backends.ldap.Identity',
        assignment_driver                  => $assignment_driver,
      }
    }
}
