# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2013, Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import os
import shutil
import tarfile
import tempfile
from unittest import TestCase

from ..test_base import PackstackTestCaseMixin
from packstack.installer.core import drones


class SshTarballTransferMixinTestCase(PackstackTestCaseMixin, TestCase):
    def setUp(self):
        # Creating a temp directory that can be used by tests
        self.tempdir = tempfile.mkdtemp()
        # prepare resource files
        res1path = os.path.join(self.tempdir, 'res1.txt')
        with open(res1path, 'w') as f:
            f.write('resource one')
        resdir = os.path.join(self.tempdir, 'resdir')
        os.mkdir(resdir)
        res2path = os.path.join(resdir, 'res2.txt')
        with open(res2path, 'w') as f:
            f.write('resource two')
        # prepare recipe files
        rec1path = os.path.join(self.tempdir, 'rec1.pp')
        with open(rec1path, 'w') as f:
            f.write('recipe one')
        recdir = os.path.join(self.tempdir, 'recdir')
        os.mkdir(recdir)
        rec2path = os.path.join(recdir, 'rec2.pp')
        with open(rec2path, 'w') as f:
            f.write('recipe two')
        # prepare class
        self.mixin = drones.SshTarballTransferMixin()
        self.mixin.node = '127.0.0.1'
        self.mixin.resource_dir = os.path.join(self.tempdir, 'remote')
        self.mixin.recipe_dir = os.path.join(self.tempdir, 'remote',
                                             'recipes')
        self.mixin.local_tmpdir = os.path.join(self.tempdir, 'loctmp')
        self.mixin.remote_tmpdir = os.path.join(self.tempdir, 'remtmp')
        self.mixin._resources = [(res1path, 'resources'),
                                 (resdir, 'resources')]
        self.mixin._recipes = {'one': [rec1path], 'two': [rec2path]}

        for i in (self.mixin.resource_dir, self.mixin.recipe_dir,
                  self.mixin.local_tmpdir, self.mixin.remote_tmpdir):
            os.mkdir(i)

    def tearDown(self):
        # remove the temp directory
        # shutil.rmtree(self.tempdir)
        pass

    def test_tarball_packing(self):
        """
        Tests packing of resources and recipes
        """
        # pack
        res_path = self.mixin._pack_resources()
        rec_path = self.mixin._pack_recipes()
        # unpack
        for pack_path in (res_path, rec_path):
            tarball = tarfile.open(pack_path)
            tarball.extractall(path=self.tempdir)
        # check content of files
        for path, content in [('resources/res1.txt', 'resource one'),
                              ('resources/resdir/res2.txt', 'resource two'),
                              ('recipes/rec1.pp', 'recipe one'),
                              ('recipes/rec2.pp', 'recipe two')]:
            with open(os.path.join(self.tempdir, path)) as f:
                fcont = f.read()
                self.assertEqual(fcont, content)
        # clean for next test
        shutil.rmtree(os.path.join(self.tempdir, 'resources'))
        shutil.rmtree(os.path.join(self.tempdir, 'recipes'))

    '''
    # uncomment this test only on local machines
    def test_transfer(self):
        """
        Tests resources transfer if sshd to 127.0.0.1 is enabled.
        """
        remtmp = self.mixin.resource_dir
        server = utils.ScriptRunner('127.0.0.1')
        try:
           server.append('echo "test"')
           server.execute()
        except ScripRuntimeError:
            return
        # transfer
        self.mixin._copy_resources()
        self.mixin._copy_recipes()
        # check content of files
        for path, content in \
                [('resources/res1.txt', 'resource one'),
                 ('resources/resdir/res2.txt', 'resource two'),
                 ('recipes/rec1.pp', 'recipe one'),
                 ('recipes/rec2.pp', 'recipe two')]:
            with open(os.path.join(remtmp, path)) as f:
                fcont = f.read()
                self.assertEqual(fcont, content)
        # clean for next test
        server = utils.ScriptRunner('127.0.0.1')
        server.append('rm -fr %s' % remtmp)
        server.execute()
    '''


class FakeDroneObserver(drones.DroneObserver):
    def __init__(self, *args, **kwargs):
        super(FakeDroneObserver, self).__init__(*args, **kwargs)
        self.log = []

    def applying(self, drone, recipe):
        """
        Drone is calling this method when it starts applying recipe.
        """
        self.log.append('applying:%s' % recipe)

    def checking(self, drone, recipe):
        """
        Drone is calling this method when it starts checking if recipe
        has been applied.
        """
        self.log.append('checking:%s' % recipe)

    def finished(self, drone, recipe):
        """
        Drone is calling this method when it's finished with recipe
        application.
        """
        # subclass must implement this method
        self.log.append('finished:%s' % recipe)


class FakeDrone(drones.Drone):
    def __init__(self, *args, **kwargs):
        super(FakeDrone, self).__init__(*args, **kwargs)
        self.log = []

    def _apply(self, recipe):
        self.log.append(recipe)

    def _finished(self, recipe):
        return True


class DroneTestCase(PackstackTestCaseMixin, TestCase):
    def setUp(self):
        super(DroneTestCase, self).setUp()
        self.observer = FakeDroneObserver()
        self.drone = FakeDrone('127.0.0.1')
        self.drone.add_recipe('/some/recipe/path1.rec')
        self.drone.add_recipe('/some/recipe/path2.rec')
        self.drone.add_recipe('/some/recipe/path3a.rec', marker='test')
        self.drone.add_recipe('/some/recipe/path3b.rec', marker='test')
        self.drone.add_recipe('/some/recipe/path4a.rec', marker='next')
        self.drone.add_recipe('/some/recipe/path4b.rec', marker='next')
        self.drone.add_recipe('/some/recipe/path5.rec')

    def test_drone_behavior(self):
        """
        Tests Drone's recipe application order.
        """
        self.drone.log = []
        self.drone.apply()

        rdir = self.drone.recipe_dir
        recpaths = [os.path.join(rdir, os.path.basename(i))
                    for i in self.drone.recipes]
        self.assertListEqual(self.drone.log, recpaths)

    def test_observer_behavior(self):
        """
        Tests DroneObserver calling.
        """
        self.drone.set_observer(self.observer)
        self.drone.apply()

        rdir = self.drone.recipe_dir.rstrip('/')
        first = ['applying:/some/recipe/path1.rec',
                 'checking:%s/path1.rec' % rdir,
                 'finished:%s/path1.rec' % rdir,
                 'applying:/some/recipe/path2.rec',
                 'checking:%s/path2.rec' % rdir,
                 'finished:%s/path2.rec' % rdir]
        last = ['applying:/some/recipe/path5.rec',
                'checking:%s/path5.rec' % rdir,
                'finished:%s/path5.rec' % rdir]
        self.assertListEqual(self.observer.log[:6], first)
        self.assertListEqual(self.observer.log[-3:], last)
        self.assertEqual(len(self.observer.log), 21)
