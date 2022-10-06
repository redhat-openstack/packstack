class packstack::amqp ()
{
  $amqp = lookup('CONFIG_AMQP_BACKEND')

  case $amqp  {
    'rabbitmq': {
      packstack::amqp::enable_rabbitmq { 'rabbitmq': }

        # The following kernel parameters help alleviate some RabbitMQ
        # connection issues

        sysctl::value { 'net.ipv4.tcp_keepalive_intvl':
          value => '1',
        }

        sysctl::value { 'net.ipv4.tcp_keepalive_probes':
          value => '5',
        }

        sysctl::value { 'net.ipv4.tcp_keepalive_time':
          value => '5',
        }
    }
    default: {}
  }
}
