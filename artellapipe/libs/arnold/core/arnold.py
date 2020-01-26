#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains utilities functions to work with Arnold
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

from tpPyUtils import decorators

import artellapipe.register


class AbstractArnold(object):

    @decorators.abstractmethod
    def load_arnold_plugin(self):
        """
        Forces the loading of the Arnold plugin if it is not already loaded
        """

        raise NotImplementedError(
            'load_arnold_plugin function for "{}" is not implemented!'.format(self.__class__.__name__))

    @decorators.abstractmethod
    def export_standin(self, *args, **kwargs):
        """
        Exports Standin file with given attributes
        """

        raise NotImplementedError(
            'export_standin function for "{}" is not implemented!'.format(self.__class__.__name__))

    @decorators.abstractmethod
    def import_standin(self, standin_file, mode='import', nodes=None, parent=None, fix_path=False,
                       namespace=None, reference=False, **kwargs):
        """
        Imports Standin into current DCC scene

        :param str standin_file: file we want to load
        :param str mode: mode we want to use to import the Standin File
        :param list(str) nodes: optional list of nodes to import
        :param parent:
        :param fix_path: bool, whether to fix path or not
        :param namespace: str
        :param reference: bool, whether to fix path or not
        :return:
        """

        raise NotImplementedError(
            'import_standin function for "{}" is not implemented!'.format(self.__class__.__name__))


@decorators.Singleton
class AbstractArnoldSingleton(AbstractArnold, object):
    def __init__(self):
        AbstractArnold.__init__(self)


artellapipe.register.register_class('Arnold', AbstractArnoldSingleton)
