
class { 'ssh::server::install': }

Class['swift'] -> Service <| |>
class { 'swift':
    # not sure how I want to deal with this shared secret
    swift_hash_suffix => '%(CONFIG_SWIFT_HASH)s',
    package_ensure    => latest,
}
