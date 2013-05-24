Facter.add(:netns_support) do
  setcode do
    oldout = $stdout.clone
    olderr = $stderr.clone
    $stdout.reopen("/dev/null", "w")
    $stderr.reopen("/dev/null", "w")

    script_path = File.join(File.dirname(__FILE__), 'netns.py')
    passed = system "python #{script_path}"

    $stdout.reopen(oldout)
    $stderr.reopen(olderr)

    passed
  end
end
