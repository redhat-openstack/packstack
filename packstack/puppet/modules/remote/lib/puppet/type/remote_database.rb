
Puppet::Type.newtype(:remote_database) do
  @doc = "Manage databases remotely."

  ensurable

  newparam(:name, :namevar=>true) do
    desc "The name of the database."
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

  newproperty(:charset) do
    desc "The characterset to use for a database"
    defaultto :utf8
    newvalue(/^\S+$/)
  end

  newproperty(:collate) do
    desc 'The collate setting for the database'
    defaultto :utf8_general_ci
    newvalue(/^\S+$/)
  end

end
