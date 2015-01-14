
# Function returns host's IP selected from list of IPs
module Puppet::Parser::Functions
  newfunction(:choose_my_ip, :type => :rvalue) do |args|

    if args.size < 1
      raise(
        Puppet::ParseError,
        "choose_my_ip(): Wrong number of arguments given (#{args.size} for 1)"
      )
    end

    host_list = args[0]
    if not host_list.kind_of?(Array)
      host_list = [host_list]
    end
    my_ips = lookupvar('interfaces').split(',').map do |interface|
        interface.strip!
        lookupvar("ipaddress_#{interface}")
    end

    result = nil
    host_list.each do |ip|
      if my_ips.include? ip
        result = ip
      end
    end
    result
  end
end
