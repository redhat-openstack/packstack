require 'facter'
Facter.add(:gateway_device) do
  setcode "awk '$2==00000000 && $8==00000000 {print $1}' /proc/net/route|sort -r -n -k 7|head -n 1"
end
