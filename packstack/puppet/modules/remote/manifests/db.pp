
class remote::db (
  $mysql_client_package        = $remote::params::mysql_client_package,
  $mysql_client_package_ensure = 'present',
) inherits remote::params {

  package { $mysql_client_package:
    ensure => $mysql_client_package_ensure,
  }

  Package[$mysql_client_package] -> Remote_database<||>
  Package[$mysql_client_package] -> Remote_database_user<||>
  Package[$mysql_client_package] -> Remote_database_grant<||>

}
