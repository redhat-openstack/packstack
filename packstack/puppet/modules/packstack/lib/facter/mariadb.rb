
# Check if mariadb provides galera server

Facter.add(:mariadb_provides_galera) do
  setcode do
    command = 'dnf repoquery --whatprovides mariadb-server-galera'
    output = Facter::Util::Resolution.exec(command)
    (output =~ /mariadb-server-galera.*/) != nil
  end
end
