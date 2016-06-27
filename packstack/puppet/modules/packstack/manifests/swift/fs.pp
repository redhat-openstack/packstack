define packstack::swift::fs (
  $device,
  $dev,
  $fstype
)
{
  case $fstype {
    'xfs':   { swift::storage::xfs {$device: device => $dev }  }
    'ext4':  { swift::storage::ext4 {$device: device => $dev }  }
    default: { fail('Unsupported fs for Swift storage') }
  }
}
