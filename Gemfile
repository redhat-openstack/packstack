source ENV["GEM_SOURCE"] || "https://rubygems.org"

group :development, :test do
  gem 'puppetlabs_spec_helper', :require => false
  gem 'puppet-lint', '~> 1.1'
  gem 'puppet-lint-param-docs', '1.1.0'
  gem 'puppet-syntax'
  gem 'rake', '10.1.1'
end

if puppetversion = ENV['PUPPET_GEM_VERSION']
  gem 'puppet', puppetversion, :require => false
else
  gem 'puppet', :require => false
end

# vim:ft=ruby
