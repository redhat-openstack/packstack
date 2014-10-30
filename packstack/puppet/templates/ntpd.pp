$cfg_ntp_server_def = hiera('CONFIG_NTP_SERVER_DEF')
$cfg_ntp_servers    = hiera('CONFIG_NTP_SERVERS')

$config_content = "
driftfile /var/lib/ntp/drift

# Permit time synchronization with our time source, but do not
# permit the source to query or modify the service on this system.
restrict default kod nomodify notrap nopeer noquery
restrict -6 default kod nomodify notrap nopeer noquery

# Permit all access over the loopback interface.  This could
# be tightened as well, but to do so would effect some of
# the administrative functions.
restrict 127.0.0.1
restrict -6 ::1

# Hosts on local network are less restricted.
#restrict 192.168.1.0 mask 255.255.255.0 nomodify notrap

# Use public servers from the pool.ntp.org project.
# Please consider joining the pool (http://www.pool.ntp.org/join.html).
${cfg_ntp_server_def}

#broadcast 192.168.1.255 autokey    # broadcast server
#broadcastclient            # broadcast client
#broadcast 224.0.1.1 autokey        # multicast server
#multicastclient 224.0.1.1      # multicast client
#manycastserver 239.255.254.254     # manycast server
#manycastclient 239.255.254.254 autokey # manycast client

# Undisciplined Local Clock. This is a fake driver intended for backup
# and when no outside source of synchronized time is available.
#server 127.127.1.0 # local clock
#fudge  127.127.1.0 stratum 10

# Enable public key cryptography.
#crypto

includefile /etc/ntp/crypto/pw

# Key file containing the keys and key identifiers used when operating
# with symmetric key cryptography.
keys /etc/ntp/keys

# Specify the key identifiers which are trusted.
#trustedkey 4 8 42

# Specify the key identifier to use with the ntpdc utility.
#requestkey 8

# Specify the key identifier to use with the ntpq utility.
#controlkey 8

# Enable writing of statistics records.
#statistics clockstats cryptostats loopstats peerstats
"

package { 'ntp':
  ensure => 'installed',
  name   => 'ntp',
}

file { 'ntp_config':
  ensure  => file,
  path    => '/etc/ntp.conf',
  mode    => '0644',
  content => $config_content,
}

# Unfortunately, the RedHat osfamily doesn't only include RHEL and
# derivatives thereof but also Fedora so further differentiation by
# operatingsystem is necessary.
$command = $osfamily ? {
  'RedHat' => $operatingsystem ? {
  'Fedora' => '/usr/bin/systemctl stop ntpd.service',
  default  => '/sbin/service ntpd stop',
  },
}

exec { 'stop-ntpd':
  command => $command,
}

exec { 'ntpdate':
  command => "/usr/sbin/ntpdate ${cfg_ntp_servers}",
  tries   => 3,
}

service { 'ntpd':
  ensure     => running,
  enable     => true,
  name       => 'ntpd',
  hasstatus  => true,
  hasrestart => true,
}

Package['ntp'] ->
File['ntp_config'] ->
Exec['stop-ntpd'] ->
Exec['ntpdate'] ->
Service['ntpd']
