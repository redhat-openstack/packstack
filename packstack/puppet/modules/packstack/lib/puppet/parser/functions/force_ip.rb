
require 'resolv'
require 'ipaddr'


module Puppet::Parser::Functions
  newfunction(:force_ip, :type => :rvalue) do |args|
    if args.size < 1
      raise(
        Puppet::ParseError,
        "force_ip(): Wrong number of arguments given (#{args.size} for 1)"
      )
    end
    if (!!IPAddr.new(args[0]) rescue false)
      args[0]
    else
      Resolv.getaddress args[0]
    end
  end
end
