# -*- coding: utf-8 -*-


def get_mq(config, plugin):
    return plugin + "_%s.pp" % config.get('CONFIG_AMQP_BACKEND')
