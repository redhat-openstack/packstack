
# Check if mariadb provides galera server

Facter.add(:mariadb_provides_galera) do
  setcode do
    if Facter.value(:operatingsystem) == 'Fedora' and Facter.value(:operatingsystemmajrelease).to_i > 22
      command = 'dnf repoquery --whatprovides mariadb-server-galera'
    else
      command = 'repoquery --whatprovides mariadb-server-galera'
    end
    output = Facter::Util::Resolution.exec(command)
    (output =~ /mariadb-server-galera.*/) != nil
  end
end
