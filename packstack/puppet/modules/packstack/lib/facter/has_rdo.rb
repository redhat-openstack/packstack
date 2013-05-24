Facter.add(:has_rdo) do
  setcode do
    system "ls /etc/yum.repos.d/rdo-release.repo"
  end
end
