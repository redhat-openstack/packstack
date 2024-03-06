Packstack
=========

Utility to install **OpenStack** on **Red Hat** based operating system.
See other branches for older **OpenStack** versions. Details on how to
contribute to **Packstack** may be found in the **Packstack** wiki at
https://wiki.openstack.org/wiki/Packstack Additional information about
involvement in the community around **Packstack** can be found at
https://openstack.redhat.com/Get_involved

This utility can be used to install **OpenStack** on a single or group
of hosts (over ``ssh``).

This utility is still in the early stages, a lot of the configuration
options have yet to be added.

Installation of packstack:
--------------------------

::

   $ yum install -y git
   $ git clone git://github.com/openstack/packstack.git
   $ cd packstack && sudo python setup.py install

Installation of Puppet modules (REQUIRED if running packstack from source):
---------------------------------------------------------------------------

::

   $ export GEM_HOME=/tmp/somedir
   $ gem install r10k
   $ sudo -E /tmp/somedir/bin/r10k puppetfile install -v
   $ sudo cp -r packstack/puppet/modules/packstack /usr/share/openstack-puppet/modules

Option 1 (all-in-one)
~~~~~~~~~~~~~~~~~~~~~

::

   $ packstack --allinone

This will install all **OpenStack** services on a single host without
prompting for any configuration information. This will generate an
“answers” file (``packstack-answers-<date>-<time>.txt``) containing all
the values used for the install.

If you need to re-run packstack, you must use the ``--answer-file``
option in order for packstack to use the correct values for passwords
and other authentication credentials:

::

   $ packstack --answer-file packstack-answers-<date>-<time>.txt

Option 2 (using answer file)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

   $ packstack --gen-answer-file=ans.txt

Then edit ``ans.txt`` as appropriate e.g.

-  set ``CONFIG_SSH_KEY`` to a public ssh key to be installed to remote
   machines
-  Edit the IP address to anywhere you want to install a piece of
   OpenStack on another server
-  Edit the 3 network interfaces to whatever makes sense in your setup

   $ packstack –answer-file=ans.txt

Option 3 (prompts for configuration options)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

   $ packstack

that’s it, if everything went well you can now start using OpenStack

::

   $ cd
   $ . keystonerc_admin
   $ nova list
   $ swift list  # if you have installed swift

Config options
--------------

-  ``CONFIG_NOVA_COMPUTE_HOSTS`` :

   -  A comma separated list of ip addresses on which to install nova
      compute

-  ``CONFIG_SWIFT_STORAGE_HOSTS`` :

   -  A comma separated list of swift storage devices

      -  ``1.1.1.1``: create a testing loopback device and use this for
         storage
      -  ``1.1.1.1/sdb``: use ``/dev/sdb`` on ``1.1.1.1`` as a storage
         device

Logging
-------

The location of the log files and generated puppet manifests are in the
``/var/tmp/packstack`` directory under a directory named by the date in
which **Packstack** was run and a random string
(e.g. ``/var/tmp/packstack/20131022-204316-Bf3Ek2``). Inside, we find a
manifest directory and the ``openstack-setup.log`` file; puppet
manifests and a log file for each one are found inside the manifest
directory.

Debugging
---------

To make **Packstack** write more detailed information into the log file
you can use the ``-d`` switch:

::

   $ packstack -d --allinone

When upgrading to a new OpenStack release and reusing old answerfile it
is useful to know if any **Packstack** option was removed. If answerfile
is written by hand it is possible to make a mistake. The
``--validate-answer-file`` switch allows checking if any provided option
is not recognized by **Packstack**.

::

   $ packstack --validate-answer-file=ans.txt

Developing
----------

To ease development of **Packstack**, it can be useful to install from
*git* such that updates to the git repositories are immediately
effective without reinstallation.

To do this, start with a minimal **CentOS 7** installation. Then remove
any relevant packages that might conflict:

::

   $ yum -y erase openstack-packstack*,puppet-*

Disable **SELinux** by changing “``enforcing``” to “``permissive``” in
``/etc/sysconfig/selinux``, then reboot to allow service changes to take
effect and swap over networking. Then install packages:

::

   $ yum -y install git python-setuptools

And install **RDO**:

::

   $ yum -y install https://www.rdoproject.org/repos/rdo-release.rpm
   $ yum -y update

Install Puppet modules as described
`above <README.md#installation-of-puppet-modules-required-if-running-packstack-from-source>`__.

Then we get **Packstack**:

::

   $ yum install -y python-crypto python-devel libffi-devel openssl-devel gcc-c++
   $ git clone https://github.com/openstack/packstack
   $ cd packstack
   $ python setup.py develop

And we’re done. Changes to the contents of **Packstack** source
repository are picked up by the **Packstack** executable without further
intervention, and **Packstack** is ready to install.

Puppet Style Guide
------------------

**IMPORTANT** https://docs.puppetlabs.com/guides/style_guide.html

Please, respect the Puppet Style Guide as much as possible !

Running local Puppet-lint tests
-------------------------------

It assumes that both ``bundler`` as well as ``rubygems`` (and ``ruby``)
are already installed on the system. If not, run this command:

::

   $ sudo yum install rubygems rubygem-bundler ruby ruby-devel -y

Go into the **Packstack** root directory.

::

   $ cd packstack/

A ``Rakefile`` contains all you need to run puppet-lint task
automatically over all the puppet manifests included in the
**Packstack** project.

::

   $ ls -l packstack/puppet/templates/

and

::

   $ ls -l packstack/puppet/modules/

The default puppet-lint pattern for ``.pp`` files is ``**/*.pp``. So
there is no need to go inside those directories to run puppet-lint !

::

   $ mkdir vendor
   $ export GEM_HOME=vendor
   $ bundle install
   $ bundle exec rake lint

Packstack integration tests
---------------------------

Packstack is integration tested in the OpenStack gate and provides the
means to reproduce these tests on your environment if you wish.

Scenario000 installs packstack allinone only and doesn’t run any tests.
This is the current matrix of available tests:

============== =========== =========== =========== ===========
-              scenario000 scenario001 scenario002 scenario003
============== =========== =========== =========== ===========
keystone       FERNET      FERNET      FERNET      FERNET
glance                     file        swift       file
nova           X           X           X           X
neutron        X           X           X           X
neutron plugin ovn         ovn         ovs         ovn
vpnaas                                            
cinder         X           X                      
ceilometer     X                                   X
aodh           X                                   X
gnocchi        X                                   X
heat                                               X
swift          X                       X          
trove                                  X          
horizon                    X                      
manila                     X                      
SSL                        X                      
============== =========== =========== =========== ===========

To run these tests:

::

   export SCENARIO="scenario001"
   ./run_tests.sh

run_tests.sh will take care of installing the required dependencies,
configure packstack to run according to the above matrix and run the
complete installation process. If the installation is successful,
tempest will also run smoke tests.

By default, run_tests.sh will set up delorean (RDO Trunk) repositories.
There are two ways of overriding default repositories:

::

   export DELOREAN="http://someotherdomain.tld/delorean.repo"
   export DELOREAN_DEPS="http://someotherdomain.tld/delorean-deps.repo"
   ./run_tests.sh

You can also choose to disable repository management entirely:

::

   <setup your own custom repositories here>
   export MANAGE_REPOS="false"
   ./run_tests.sh

Reporting Bugs
--------------

Bugs for packstack are tracked in the "packstack" component of the [RDO Jira board](https://issues.redhat.com/issues/?jql=project+%3D+RDO+AND+component+%3D+packstack).
If you find issues, you can create an issue on that board and provide the relevant information to describe your problem.

