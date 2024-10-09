Puppet::Functions.create_function(:parse_hash_from_string) do
  def parse_hash_from_string(*args)
    if args.length > 1
      raise Puppet::Error, 'Argument must be one'
    elsif !(args[0].kind_of?(String))
      raise Puppet::Error, 'Argument must be a string'
    end

    value = args[0]
    return Hash[value.scan(/(\S+)='([^']*)'/)]
  end
end
