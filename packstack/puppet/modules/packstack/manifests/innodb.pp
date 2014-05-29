#
# author: Martin Magr <mmagr@redhat.com>
#
# == Class: packstack::innodb
#
# Changes mysql/mariadb configuration for better performance
#
# === Parameters
#
# [*buffer_pool_size*]
#   Value for innodb_buffer_pool_size in my.cnf config file. Defaults to 20%
#   of available memory
#
# [*log_file_size*]
#   Value for innodb_log_file_size in my.cnf config file. Defaults to 25%
#   of buffer_pool_size
#
# [*clean*]
#   Clean mysql logs before changing log configuration.
#

class packstack::innodb (
  $buffer_pool_size = $::innodb_bufferpoolsize,
  $log_file_size = $::innodb_logfilesize,
  $clean = true,
)
{

  if $clean {
    exec { 'clean_innodb_logs':
      path    => ['/usr/bin', '/bin', '/usr/sbin', '/sbin'],
      command => "service mysqld stop && rm -f /var/lib/mysql/ib_logfile?",
      onlyif  => "ls  /var/lib/mysql/ib_logfile?",
      notify  => Service['mysqld'],
      logoutput => 'on_failure',
      subscribe => File['/etc/my.cnf.d/innodb.cnf'],
      refreshonly => true,
    }
  }

  file { '/etc/my.cnf.d/innodb.cnf':
    require => Package["$mysql::server::package_name"],
    content => template('packstack/innodb.cnf.erb'),
    mode    => '0644',
    notify  => Service['mysqld'],
  }

}
