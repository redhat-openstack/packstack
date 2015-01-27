# Code common to all classes that use Apache
#
# This allows multiple modules to safely use ::apache without
# overwriting existing config or the ports file.
#
# Any module that uses apache must include this class
#   include packstack_apache_common
class packstack::apache_common {
  include ::apache::params
  # make sure the include ::apache in the module
  # does not overwrite the contents of the config dirs
  # from a previous module
  if $::apache::params::confd_dir {
    File<| title == $::apache::params::confd_dir |> {
      purge => false,
    }
  }
  # make sure the ports.conf concat fragments from previous
  # runs are not overwritten by subsequent runs
  include ::concat::setup
  $my_safe_name = regsubst($::apache::params::ports_file, '[/:]', '_', 'G')
  $my_fragdir = "${concat::setup::concatdir}/${my_safe_name}"
  File<| title == "${my_fragdir}/fragments" |> {
    purge => false,
  }
}
