# See the qdrouterd.conf (5) manual page for information about this
# file's format and options.

container {
    worker-threads: $container_worker_threads
    container-name: $container_name
}

ssl-profile {
    name: $ssl_profile_name
}

listener {
    addr: $listen_address
    port: listen_$port
    sasl-mechanisms: $sasl_mechanisms
}

router {
    mode: $router_mode
    router-id: $router_id
}
