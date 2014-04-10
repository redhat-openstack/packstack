
class { "nova":
    glance_api_servers => "%(CONFIG_GLANCE_HOST)s:9292",
    rabbit_host        => "%(CONFIG_AMQP_HOST)s",
    rabbit_port        => '%(CONFIG_AMQP_CLIENTS_PORT)s',
    rabbit_userid      => '%(CONFIG_AMQP_AUTH_USER)s',
    rabbit_password    => '%(CONFIG_AMQP_AUTH_PASSWORD)s',
    verbose            => true,
    debug              => %(CONFIG_DEBUG_MODE)s,
    nova_public_key    => {
      type             => '%(NOVA_MIGRATION_KEY_TYPE)s',
      key              => '%(NOVA_MIGRATION_KEY_PUBLIC)s',
    },
    nova_private_key   => {
      type             => '%(NOVA_MIGRATION_KEY_TYPE)s',
      key              => '%(NOVA_MIGRATION_KEY_SECRET)s',
    },
    nova_shell => '/bin/bash',
}
