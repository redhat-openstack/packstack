sshkey { '%(SSH_HOST_NAME)s':
  ensure       => present,
  host_aliases => [%(SSH_HOST_ALIASES)s],
  key          => '%(SSH_HOST_KEY)s',
  type         => '%(SSH_HOST_KEY_TYPE)s',
}

