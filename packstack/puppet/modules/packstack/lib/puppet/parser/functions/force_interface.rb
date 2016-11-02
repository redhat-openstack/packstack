
require 'ipaddr'

# Returns value
module Puppet::Parser::Functions
  newfunction(:force_interface, :type => :rvalue) do |args|

    if args.size < 2
      raise(
        Puppet::ParseError,
        "force_interface(): Wrong number of arguments given (#{args.size} for 2)"
      )
    end

    value = args[0]
    allow = args[1]

    was_array = value.kind_of?(Array)
    if not was_array
      value = [value]
    end

    result = []
    if allow
      value.each do |val|
        translated = []
        val.split(':').each do |fragment|
          if fragment.include?('/') # this is CIDR, so translate it
            cidr = IPAddr.new fragment
            lookupvar('interfaces').split(',').each do |interface|
              interface.strip!
              ifaddr = lookupvar("ipaddress_#{interface}")
              if ifaddr == nil
                next
              end
              ifcidr = IPAddr.new ifaddr
              if cidr.include?(ifcidr)
                translated.push(interface)
              end
            end
          else
            translated.push(fragment)
          end
        end
        result.push(translated.join(':'))
      end
    else
      result = value
    end
    if not was_array
      result = result[0]
    end
    result
  end
end
