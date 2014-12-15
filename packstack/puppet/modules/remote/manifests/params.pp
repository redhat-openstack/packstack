
class remote::params {

  case $::osfamily {
    'RedHat': {
      case $::operatingsystem {

        'Fedora': {
          $mysql_client_package = 'mariadb'
        }

        'RedHat', 'CentOS', 'Scientific': {
          if $::operatingsystemmajrelease >= 7 {
            $mysql_client_package = 'mariadb'
          } else {
            $mysql_client_package = 'mysql'
          }
        }

        default: {
          $mysql_client_package = 'mysql'
        }
      }
    }

    'Debian': {
      $mysql_client_package = 'mysql'
    }

    default: {
      fail("Unsupported platform")
    }
  }
}
