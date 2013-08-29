# -*- coding: utf-8 -*-


def host_iter(config):
    for key, value in config.iteritems():
        if key.endswith("_HOST"):
            host = value.split('/')[0]
            yield key, host
        if key.endswith("_HOSTS"):
            for i in value.split(","):
                host = i.strip().split('/')[0]
                yield key, host


def hosts(config):
    result = set()
    for key, host in host_iter(config):
        result.add(host)
    return result
