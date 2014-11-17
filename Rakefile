require 'puppetlabs_spec_helper/rake_tasks'
require 'puppet-lint/tasks/puppet-lint'
require 'puppet-syntax/tasks/puppet-syntax'

PuppetLint.configuration.relative = true
PuppetLint.configuration.log_format = "%{path}:%{linenumber}:%{check}:%{KIND}:%{message}"
PuppetLint.configuration.fail_on_warnings = true
PuppetLint.configuration.send('disable_class_parameter_defaults')
PuppetLint.configuration.send('disable_class_inherits_from_params_class')
PuppetLint.configuration.send('disable_80chars')
PuppetLint.configuration.send('disable_containing_dash')
PuppetLint.configuration.send('disable_quoted_booleans')
PuppetLint.configuration.send('disable_documentation')

exclude_paths = [
"pkg/**/*",
"vendor/**/*",
"spec/**/*",
]

Rake::Task[:lint].clear
PuppetLint.configuration.ignore_paths = exclude_paths
PuppetSyntax.exclude_paths = exclude_paths

desc "Run syntax, lint"
task :test => [
  :syntax,
  :lint,
]
