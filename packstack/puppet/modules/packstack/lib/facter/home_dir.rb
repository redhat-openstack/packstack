
# Current users home directory

Facter.add("home_dir") do
  setcode do
    Facter::Util::Resolution.exec('/bin/echo $HOME')
  end
end
