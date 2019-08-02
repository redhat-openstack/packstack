
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
    my_ips = Array.new
    lookupvar('interfaces').split(',').each do |interface|
        interface.strip!
        my_ips.push(lookupvar("ipaddress_#{interface}"))
        my_ips.push(lookupvar("ipaddress6_#{interface}"))
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
