Facter.add(:innodb_logfilesize) do
  setcode do
    buffsize = Float(Facter.value('innodb_bufferpoolsize'))
    Integer(buffsize * 0.25)
  end
end
