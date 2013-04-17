
package { 'mysql':
    ensure => 'present',
}

Package ['mysql'] -> Remote_database<||>
Package ['mysql'] -> Remote_database_user<||>
Package ['mysql'] -> Remote_database_grant<||>
