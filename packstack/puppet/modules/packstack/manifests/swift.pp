class packstack::swift ()
{
    # Class['swift'] -> Service <| |>

    class { '::swift':
      # not sure how I want to deal with this shared secret
      swift_hash_path_suffix => hiera('CONFIG_SWIFT_HASH'),
      package_ensure         => latest,
    }
}
