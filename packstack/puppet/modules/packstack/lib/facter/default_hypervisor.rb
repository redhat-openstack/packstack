
# Custom fact to keep backwards compatibility to default to qemu when the
# is_virtual fact is true and otherwise default to kvm
# This fact is then used as a default value for the
# CONFIG_NOVA_LIBVIRT_VIRT_TYPE packstack parameter.

Facter.add(:default_hypervisor) do
  setcode do
    if Facter.value(:is_virtual) == true
      output = 'qemu'
    else
      output = 'kvm'
    end
    output
  end
end
