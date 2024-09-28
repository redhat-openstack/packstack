# -*- coding: utf-8 -*-
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import os
import shutil
import stat
import tarfile
import tempfile
import time
import uuid

from .. import utils


class SshTarballTransferMixin(object):
    """
    Transfers resources and recipes by packing them to tar.gz and
    copying it via ssh.
    """
    def _transfer(self, pack_path, pack_dest, res_dir):
        node = self.node
        args = locals()
        # copy and extract tarball
        script = utils.ScriptRunner()
        script.append("scp %(pack_path)s root@%(node)s:%(pack_dest)s"
                      % args)
        script.append("ssh -o StrictHostKeyChecking=no "
                      "-o UserKnownHostsFile=/dev/null root@%(node)s "
                      "tar -C %(res_dir)s -xpzf %(pack_dest)s" % args)
        try:
            script.execute()
        except utils.ScriptRuntimeError as ex:
            # TO-DO: change to appropriate exception
            raise RuntimeError('Failed to copy resources to node %s. '
                               'Reason: %s' % (node, ex))

    def _pack_resources(self):
        randpart = uuid.uuid4().hex[:8]
        pack_path = os.path.join(self.local_tmpdir,
                                 'res-%s.tar.gz' % randpart)
        pack = tarfile.open(pack_path, mode='w:gz')
        os.chmod(pack_path, stat.S_IRUSR | stat.S_IWUSR)
        for path, dest in self._resources:
            if not dest:
                dest = os.path.basename(path)
            pack.add(path,
                     arcname=os.path.join(dest, os.path.basename(path)))
        pack.close()
        return pack_path

    def _copy_resources(self):
        pack_path = self._pack_resources()
        pack_dest = os.path.join(self.remote_tmpdir,
                                 os.path.basename(pack_path))
        self._transfer(pack_path, pack_dest, self.resource_dir)

    def _pack_recipes(self):
        randpart = uuid.uuid4().hex[:8]
        pack_path = os.path.join(self.local_tmpdir,
                                 'rec-%s.tar.gz' % randpart)
        pack = tarfile.open(pack_path, mode='w:gz')
        os.chmod(pack_path, stat.S_IRUSR | stat.S_IWUSR)
        if self.recipe_dir.startswith(self.resource_dir):
            dest = self.recipe_dir[len(self.resource_dir):].lstrip('/')
        else:
            dest = ''
        for marker, recipes in self._recipes.items():
            for path in recipes:
                _dest = os.path.join(dest, os.path.basename(path))
                pack.add(path, arcname=_dest)
        pack.close()
        return pack_path

    def _copy_recipes(self):
        pack_path = self._pack_recipes()
        pack_dest = os.path.join(self.remote_tmpdir,
                                 os.path.basename(pack_path))
        if self.recipe_dir.startswith(self.resource_dir):
            extr_dest = self.resource_dir
        else:
            extr_dest = self.recipe_dir
        self._transfer(pack_path, pack_dest, extr_dest)


class DroneObserver(object):
    """
    Base class for listening messages from drones.
    """
    def applying(self, drone, recipe):
        """
        Drone is calling this method when it starts applying recipe.
        """
        # subclass must implement this method
        raise NotImplementedError()

    def checking(self, drone, recipe):
        """
        Drone is calling this method when it starts checking if recipe
        has been applied.
        """
        # subclass must implement this method
        raise NotImplementedError()

    def finished(self, drone, recipe):
        """
        Drone is calling this method when it's finished with recipe
        application.
        """
        # subclass must implement this method
        raise NotImplementedError()


class Drone(object):
    """
    Base class used to apply installation recipes to nodes.
    """
    def __init__(self, node, resource_dir=None, recipe_dir=None,
                 local_tmpdir=None, remote_tmpdir=None):
        self._recipes = utils.SortedDict()
        self._resources = []
        self._applied = set()
        self._running = set()
        self._observer = None

        # remote host IP or hostname
        self.node = node
        # working directories on remote host
        self.resource_dir = (resource_dir or
                             '/tmp/drone%s' % uuid.uuid4().hex[:8])
        self.recipe_dir = (recipe_dir or
                           os.path.join(self.resource_dir, 'recipes'))
        # temporary directories
        self.remote_tmpdir = (remote_tmpdir or
                              '/tmp/drone%s' % uuid.uuid4().hex[:8])
        self.local_tmpdir = (local_tmpdir or
                             tempfile.mkdtemp(prefix='drone'))

    def init_node(self):
        """
        Initializes node for manipulation.
        """
        created = []
        server = utils.ScriptRunner(self.node)
        for i in (self.resource_dir, self.recipe_dir,
                  self.remote_tmpdir):
            server.append('mkdir -p %s' % os.path.dirname(i))
            server.append('mkdir --mode 0700 %s' % i)
            created.append('%s:%s' % (self.node, i))
        server.execute()

        # TO-DO: complete logger name when logging will be setup correctly
        logger = logging.getLogger()
        logger.debug('Created directories: %s' % ','.join(created))

    @property
    def recipes(self):
        for i in self._recipes.itervalues():
            for y in i:
                yield y

    @property
    def resources(self):
        for i in self._resources:
            yield i[0]

    def add_recipe(self, path, marker=None):
        """
        Registers recipe for application on node. Recipes will be
        applied in order they where added to drone. Multiple recipes can
        be applied in paralel if they have same marker.
        """
        marker = marker or uuid.uuid4().hex[:8]
        self._recipes.setdefault(marker, []).append(path)

    def add_resource(self, path, destination=None):
        """
        Registers resource. Destination will be relative from resource
        directory on node.
        """
        dest = destination or ''
        self._resources.append((path, dest))

    def _copy_resources(self):
        """
        Copies all local files registered in self._resources to their
        appropriate destination on self.node. If tmpdir is given this
        method can operate only in this directory.
        """
        # subclass must implement this method
        raise NotImplementedError()

    def _copy_recipes(self):
        """
        Copies all local files registered in self._recipes to their
        appropriate destination on self.node. If tmpdir is given this
        method can operate only in this directory.
        """
        # subclass must implement this method
        raise NotImplementedError()

    def prepare_node(self):
        """
        Copies all local resources and recipes to self.node.
        """
        # TO-DO: complete logger name when logging will be setup correctly
        logger = logging.getLogger()
        logger.debug('Copying drone resources to node %s: %s'
                     % (self.node, self.resources))
        self._copy_resources()
        logger.debug('Copying drone recipes to node %s: %s'
                     % (self.node, [i[0] for i in self.recipes]))
        self._copy_recipes()

    def _apply(self, recipe):
        """
        Starts application of single recipe given as path to the recipe
        file in self.node. This method should not wait until recipe is
        applied.
        """
        # subclass must implement this method
        raise NotImplementedError()

    def _finished(self, recipe):
        """
        Returns True if given recipe is applied, otherwise returns False
        """
        # subclass must implement this method
        raise NotImplementedError()

    def _wait(self):
        """
        Waits until all started applications of recipes will be finished
        """
        while self._running:
            _run = list(self._running)
            for recipe in _run:
                if self._observer:
                    self._observer.checking(self, recipe)
                if self._finished(recipe):
                    self._applied.add(recipe)
                    self._running.remove(recipe)
                    if self._observer:
                        self._observer.finished(self, recipe)
                else:
                    time.sleep(3)
                    continue

    def set_observer(self, observer):
        """
        Registers an observer. Given object should be subclass of class
        DroneObserver.
        """
        for attr in ('applying', 'checking', 'finished'):
            if not hasattr(observer, attr):
                raise ValueError('Observer object should be a subclass '
                                 'of class DroneObserver.')
        self._observer = observer

    def apply(self, marker=None, name=None, skip=None):
        """
        Applies recipes on node. If marker is specified, only recipes
        with given marker are applied. If name is specified only recipe
        with given name is applied. Skips recipes with names given
        in list parameter skip.
        """
        # TO-DO: complete logger name when logging will be setup correctly
        logger = logging.getLogger()
        skip = skip or []
        lastmarker = None
        for mark, recipelist in self._recipes.items():
            if marker and marker != mark:
                logger.debug('Skipping marker %s for node %s.' %
                             (mark, self.node))
                continue
            for recipe in recipelist:
                base = os.path.basename(recipe)
                if (name and name != base) or base in skip:
                    logger.debug('Skipping recipe %s for node %s.' %
                                 (recipe, self.node))
                    continue

                # if the marker has changed then we don't want to
                # proceed until all of the previous puppet runs have
                # finished
                if lastmarker and lastmarker != mark:
                    self._wait()
                lastmarker = mark

                logger.debug('Applying recipe %s to node %s.' %
                             (base, self.node))
                rpath = os.path.join(self.recipe_dir, base)
                if self._observer:
                    self._observer.applying(self, recipe)
                self._running.add(rpath)
                self._apply(rpath)
        self._wait()

    def cleanup(self, resource_dir=True, recipe_dir=True):
        """
        Removes all directories created by this drone.
        """
        shutil.rmtree(self.local_tmpdir, ignore_errors=True)
        server = utils.ScriptRunner(self.node)
        server.append('rm -fr %s' % self.remote_tmpdir)
        if recipe_dir:
            server.append('rm -fr %s' % self.recipe_dir)
        if resource_dir:
            server.append('rm -fr %s' % self.resource_dir)
        server.execute()


class PackstackDrone(SshTarballTransferMixin, Drone):
    """
    This drone uses Puppet and it's manifests to manipulate node.
    """
    # XXX: Since this implementation is Packstack specific (_apply
    #      method), it should be moved out of installer when
    #      Controller and plugin system will be refactored and installer
    #      will support projects.
    def __init__(self, *args, **kwargs):
        kwargs['resource_dir'] = ('/var/tmp/packstack/drone%s'
                                  % uuid.uuid4().hex[:8])
        kwargs['recipe_dir'] = '%s/manifests' % kwargs['resource_dir']
        kwargs['remote_tmpdir'] = '%s/temp' % kwargs['resource_dir']

        super(PackstackDrone, self).__init__(*args, **kwargs)

        self.module_dir = os.path.join(self.resource_dir, 'modules')
        self.fact_dir = os.path.join(self.resource_dir, 'facts')

    def init_node(self):
        """
        Initializes node for manipulation.
        """
        super(PackstackDrone, self).init_node()
        server = utils.ScriptRunner(self.node)
        for pkg in ("puppet", "openssh-clients", "tar"):
            server.append(f"rpm -q --whatprovides {pkg} || "
                          f"yum install -y {pkg}")
        server.execute()

    def add_resource(self, path, resource_type=None):
        """
        Resource type should be module, fact or resource.
        """
        resource_type = resource_type or 'resource'
        dest = '%ss' % resource_type
        super(PackstackDrone, self).add_resource(path, destination=dest)

    def _finished(self, recipe):
        recipe_base = os.path.basename(recipe)
        log = os.path.join(self.recipe_dir,
                           recipe_base.replace(".finished", ".log"))
        local = utils.ScriptRunner()
        local.append('scp -o StrictHostKeyChecking=no '
                     '-o UserKnownHostsFile=/dev/null '
                     'root@%s:%s %s' % (self.node, recipe, log))
        try:
            # once a remote puppet run has finished, we retrieve
            # the log file and check it for errors
            local.execute(log=False)
            # if we got to this point the puppet apply has finished
            return True
        except utils.ScriptRuntimeError:
            # the test raises an exception if the file doesn't exist yet
            return False

    def _apply(self, recipe):
        running = "%s.running" % recipe
        finished = "%s.finished" % recipe

        server = utils.ScriptRunner(self.node)
        server.append("touch %s" % running)
        server.append("chmod 600 %s" % running)

        # XXX: This is terrible hack, but unfortunatelly the apache
        # puppet module doesn't work if we set FACTERLIB
        # https://github.com/puppetlabs/puppetlabs-apache/pull/138
        for bad_word in ('horizon', 'nagios', 'apache'):
            if bad_word in recipe:
                break
        else:
            server.append("export FACTERLIB=$FACTERLIB:%s" %
                          self.fact_dir)
        server.append("export PACKSTACK_VAR_DIR=%s" % self.resource_dir)

        # TO-DO: complete logger name when logging will be setup correctly
        logger = logging.getLogger()
        loglevel = logger.level <= logging.DEBUG and '--debug' or ''
        rdir = self.resource_dir
        mdir = self._module_dir
        server.append(
            f"( flock {rdir}/ps.lock "
            f"puppet apply {loglevel} --modulepath {mdir} "
            f"{recipe} > {running} 2>&1 < /dev/null; "
            f"mv {running} {finished} ) "
            "> /dev/null 2>&1 < /dev/null &")
        server.execute()
