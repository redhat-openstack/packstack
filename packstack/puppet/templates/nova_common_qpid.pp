
class { "nova":
    glance_api_servers => "%(CONFIG_GLANCE_HOST)s:9292",
    qpid_hostname      => "%(CONFIG_AMQP_HOST)s",
    qpid_username      => '%(CONFIG_AMQP_AUTH_USER)s',
    qpid_password      => '%(CONFIG_AMQP_AUTH_PASSWORD)s',
    rpc_backend        => 'nova.openstack.common.rpc.impl_qpid',
    qpid_port          => '%(CONFIG_AMQP_CLIENTS_PORT)s',
    qpid_protocol      => '%(CONFIG_AMQP_PROTOCOL)s',
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
