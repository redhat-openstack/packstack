Facter.add(:innodb_bufferpoolsize) do
  setcode do
    memsize = Float(Facter.value('memorysize_mb'))
    Integer(memsize * 0.2)
  end
end
