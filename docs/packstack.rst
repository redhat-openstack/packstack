=========
Packstack
=========

SYNOPSIS
========

packstack [options]

DESCRIPTION
===========

Packstack is a utility that uses uses puppet modules to install OpenStack. It can be used to install each openstack service on separate servers, all on one server or any combination of these. There are 3 ways that Packstack can be run.

- packstack
- packstack [options]
- packstack --gen-answer-file=<file>  / packstack --answer-file=<file>

The third option allows the user to generate a default answer file, edit the default options and finally run Packstack a second time using this answer file. This is the easiest way to run Packstack and the one that will be documented here. When <file> is created the OPTIONS below will be contained and can be edited by the user.

OPTIONS
=======

.. include:: general_options.rst



Log files and Debug info
------------------------

The location of the log files and generated puppet manifests are in the /var/tmp/packstack directory under a directory named by the date in which packstack was run and a random string (e.g. /var/tmp/packstack/20131022-204316-Bf3Ek2). Inside, we find a manifest directory and the openstack-setup.log file; puppet manifests and a log file for each one are found inside the manifest directory.

In case debugging info is needed while running packstack the -d switch will make it write more detailed information about the installation.

Examples:

If we need an allinone debug session:

packstack -d --allinone

If we need a answer file to tailor it and then debug:

packstack --gen-answer-file=ans.txt
packstack -d --answer-file=ans.txt


SOURCE
======
* `packstack      https://github.com/stackforge/packstack`
* `puppet modules https://github.com/puppetlabs and https://github.com/packstack`

