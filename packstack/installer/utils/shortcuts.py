# -*- coding: utf-8 -*-

import grp
import os
import pwd


def host_iter(config):
    for key, value in config.iteritems():
        if key.endswith("_HOST"):
            host = value.split('/')[0]
            if host:
                yield key, host
        if key.endswith("_HOSTS"):
            for i in value.split(","):
                host = i.strip().split('/')[0]
                if host:
                    yield key, host


def hosts(config):
    result = set()
    for key, host in host_iter(config):
        result.add(host)
    return result


def get_current_user():
    try:
        user = pwd.getpwnam(os.getlogin())
        uid, gid = user.pw_uid, user.pw_gid
    except OSError:
        # in case program is run by a script
        uid, gid = os.getuid(), os.getgid()
    return uid, gid


def get_current_username():
    uid, gid = get_current_user()
    user = pwd.getpwuid(uid).pw_name
    group = grp.getgrgid(gid).gr_name
    return user, group


def split_hosts(hosts_string):
    hosts = set()
    for host in hosts_string.split(','):
        shost = host.strip()
        if shost:
            hosts.add(shost)
    return hosts
