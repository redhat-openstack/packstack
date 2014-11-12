require 'puppetlabs_spec_helper/rake_tasks'
require 'puppet-lint/tasks/puppet-lint'
require 'puppet-syntax/tasks/puppet-syntax'

PuppetLint.configuration.fail_on_warnings = true
PuppetLint.configuration.with_filename = false
PuppetLint.configuration.send('disable_names_containing_dash')
PuppetLint.configuration.send('disable_80chars')
PuppetLint.configuration.send('disable_class_parameter_defaults')
exclude_paths = ['spec/**/*','pkg/**/*','vendor/**/*']
exclude_lint_paths = exclude_paths

PuppetLint.configuration.ignore_paths = exclude_lint_paths
PuppetSyntax.exclude_paths = exclude_paths

task(:default).clear
task :default => :lint

desc 'Run syntax, lint'
task :test => [:syntax,:lint]
