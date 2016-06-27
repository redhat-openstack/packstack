class packstack::nova::cert ()
{
    class { '::nova::cert':
      enabled => true,
    }
}
