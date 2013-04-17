Puppet::Type.type(:remote_database_user).provide(:mysql) do

  desc "manage users for a mysql database."

  defaultfor :kernel => 'Linux'

  optional_commands :mysql      => 'mysql'
  optional_commands :mysqladmin => 'mysqladmin'

  def self.instances
    users = mysql("--host=#{@resource[:db_host]}", "--user=#{@resource[:db_user]}", "--password=#{@resource[:db_password]}",
                  "mysql", '-BNe', "select concat(User, '@', Host) as User from mysql.user").split("\n")
    users.select{ |user| user =~ /.+@/ }.collect do |name|
      new(:name => name)
    end
  end

  def create
    mysql("--host=#{@resource[:db_host]}", "--user=#{@resource[:db_user]}", "--password=#{@resource[:db_password]}",
          "mysql", "-e", "create user '%s' identified by PASSWORD '%s'" % [ @resource[:name].sub("@", "'@'"), @resource.value(:password_hash) ])
  end

  def destroy
    mysql("--host=#{@resource[:db_host]}", "--user=#{@resource[:db_user]}", "--password=#{@resource[:db_password]}",
          "mysql", "-e", "drop user '%s'" % @resource.value(:name).sub("@", "'@'") )
  end

  def password_hash
    mysql("--host=#{@resource[:db_host]}", "--user=#{@resource[:db_user]}", "--password=#{@resource[:db_password]}",
          "mysql", "-NBe", "select password from mysql.user where CONCAT(user, '@', host) = '%s'" % @resource.value(:name)).chomp
  end

  def password_hash=(string)
    mysql("--host=#{@resource[:db_host]}", "--user=#{@resource[:db_user]}", "--password=#{@resource[:db_password]}",
          "mysql", "-e", "SET PASSWORD FOR '%s' = '%s'" % [ @resource[:name].sub("@", "'@'"), string ] )
  end

  def exists?
    not mysql("--host=#{@resource[:db_host]}", "--user=#{@resource[:db_user]}", "--password=#{@resource[:db_password]}",
              "mysql", "-NBe", "select '1' from mysql.user where CONCAT(user, '@', host) = '%s'" % @resource.value(:name)).empty?
  end

  def flush
    @property_hash.clear
    mysqladmin("--host=#{@resource[:db_host]}", "--user=#{@resource[:db_user]}", "--password=#{@resource[:db_password]}", "flush-privileges")
  end

end
