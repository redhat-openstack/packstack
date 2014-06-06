# Create firewall rules to allow only the FIREWALL_ALLOWED
# hosts that need to connect via FIREWALL_PORTS
# using FIREWALL_CHAIN

packstack::firewall {'%(FIREWALL_SERVICE_ID)s':
  host => %(FIREWALL_ALLOWED)s,
  service_name => '%(FIREWALL_SERVICE_NAME)s',
  chain => '%(FIREWALL_CHAIN)s',
  ports => %(FIREWALL_PORTS)s,
  proto => '%(FIREWALL_PROTOCOL)s',
}
