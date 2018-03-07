# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from docutils import core


# ------------------ helpers to locate option list ------------------ #
def _iter_by_titles(tree):
    for i in tree.children:
        i = i.asdom()
        for child in i.childNodes:
            if child.nodeName != 'title':
                continue
            if child.childNodes and child.childNodes[0].nodeValue:
                title = child.childNodes[0].nodeValue
                yield title, i


def _get_options(tree, section):
    for title, node in _iter_by_titles(tree):
        if title == section:
            return node


# --------------------- helper to locate options -------------------- #
def _iter_options(section):
    for subsection in section.childNodes:
        for subsub in subsection.childNodes:
            if subsub.nodeName != 'definition_list':
                # TO-DO: log parsing warning
                continue
            for defitem in subsub.childNodes:
                key_node = defitem.getElementsByTagName('strong')
                val_node = defitem.getElementsByTagName('paragraph')
                if not key_node or not val_node:
                    # TO-DO: log parsing warning
                    continue
                key_node = key_node[0].childNodes[0]
                val_node = val_node[0].childNodes[0]
                yield key_node.nodeValue, val_node.nodeValue


# ----------------------------- interface --------------------------- #
_rst_cache = {}


def update_params_usage(path, params, opt_title='OPTIONS', sectioned=True):
    """Updates params dict with USAGE texts parsed from given rst file."""
    def _update(section, rst):
        for param in section:
            if param['CONF_NAME'] not in rst:
                # TO-DO: log warning
                continue
            param['USAGE'] = rst[param['CONF_NAME']]

    if not _rst_cache:
        tree = core.publish_doctree(
            source=open(path).read(), source_path=path
        )
        for key, value in _iter_options(_get_options(tree, opt_title)):
            _rst_cache.setdefault(key, value)

    if sectioned:
        for section in params.values():
            _update(section, _rst_cache)
    else:
        _update(params, _rst_cache)
