
# is_virtual doesn't seem to work on all kvm vm's
# this custom one seem to do better

Facter.add("is_virtual_packstack") do
  setcode do
    Facter::Util::Resolution.exec('grep hypervisor /proc/cpuinfo > /dev/null && echo true || echo false')
  end
end
