
require 'resolv'


module Puppet::Parser::Functions
  newfunction(:force_ip, :type => :rvalue) do |args|
    if args.size < 1
      raise(
        Puppet::ParseError,
        "force_ip(): Wrong number of arguments given (#{args.size} for 1)"
      )
    end
    Resolv.getaddress args[0]
  end
end
