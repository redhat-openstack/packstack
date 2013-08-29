
Puppet::Type.newtype(:remote_database_grant) do
  @doc = "Manage a database user's rights remotely."
  #ensurable

  autorequire :remote_database do
    # puts "Starting db autoreq for %s" % self[:name]
    reqs = []
    matches = self[:name].match(/^([^@]+)@([^\/]+)\/(.+)$/)
    unless matches.nil?
      reqs << matches[3]
    end
    # puts "Autoreq: '%s'" % reqs.join(" ")
    reqs
  end

  autorequire :remote_database_user do
    # puts "Starting user autoreq for %s" % self[:name]
    reqs = []
    matches = self[:name].match(/^([^@]+)@([^\/]+).*$/)
    unless matches.nil?
      reqs << "%s@%s" % [ matches[1], matches[2] ]
    end
    # puts "Autoreq: '%s'" % reqs.join(" ")
    reqs
  end

  newparam(:name, :namevar=>true) do
    desc "The primary key: either user@host for global privilges or user@host/database for database specific privileges"
  end

  newparam(:db_host) do
    desc "The hostname of the database server to connect."
  end

  newparam(:db_user) do
    desc "The user name to use when connecting to the server."
  end

  newparam(:db_password) do
    desc "The password with which to connect to the database server."
  end

  newproperty(:privileges, :array_matching => :all) do
    desc "The privileges the user should have. The possible values are implementation dependent."

    def should_to_s(newvalue = @should)
      if newvalue
        unless newvalue.is_a?(Array)
          newvalue = [ newvalue ]
        end
        newvalue.collect do |v| v.downcase end.sort.join ", "
      else
        nil
      end
    end

    def is_to_s(currentvalue = @is)
      if currentvalue
        unless currentvalue.is_a?(Array)
          currentvalue = [ currentvalue ]
        end
        currentvalue.collect do |v| v.downcase end.sort.join ", "
      else
        nil
      end
    end

    # use the sorted outputs for comparison
    def insync?(is)
      if defined? @should and @should
        case self.should_to_s
        when "all"
          self.provider.all_privs_set?
        when self.is_to_s(is)
          true
        else
          false
        end
      else
        true
      end
    end
  end

end
