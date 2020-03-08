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

from tpDcc.libs.python import decorators

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
    def get_asset_operator(self, asset_id, connect_to_scene_operator=True, create=True):
        """
        Creates asset operator node with the given name
        :param asset_id: str
        :param connect_to_scene_operator: bool
        :param create: bool
        :return: str or None
        """

        raise NotImplementedError(
            'get_asset_operator function for "{}" is not implemented!'.format(self.__class__.__name__))

    @decorators.abstractmethod
    def get_asset_shape_operator(self, asset_id, asset_shape, connect_to_asset_operator=True, create=True):
        """
        Creates asset shape operator node with the given name
        :param asset_id: str
        :param asset_shape: str
        :param connect_to_asset_operator: bool
        :param create: bool
        :return: str or None
        """

        raise NotImplementedError(
            'get_asset_shape_operator function for "{}" is not implemented!'.format(self.__class__.__name__))

    @decorators.abstractmethod
    def get_scene_operator(self):
        """
        Returns Arnold scene operator node. The node is created if it does already exists
        :return:
        """

        raise NotImplementedError(
            'get_scene_operator function for "{}" is not implemented!'.format(self.__class__.__name__))

    @decorators.abstractmethod
    def remove_scene_operator(self):
        """
        Removes Arnold scene operator node if exists
        :return:
        """

        raise NotImplementedError(
            'remove_scene_operator function for "{}" is not implemented!'.format(self.__class__.__name__))

    @decorators.abstractmethod
    def connect_asset_operator_to_scene_operator(self, asset_operator_name):
        """
        Connects given asset operator node to the scene operator node
        :param asset_operator_name: str
        :return: bool
        """

        raise NotImplementedError(
            'connect_asset_operator_to_scene_operator function for "{}" is not implemented!'.format(
                self.__class__.__name__))

    @decorators.abstractmethod
    def connect_asset_shape_operator_to_asset_operator(self, asset_shape_operator_name):
        """
        Connects given asset shape operator node to the asset operator node
        :param asset_shape_operator_name: str
        :return: bool
        """

        raise NotImplementedError(
            'connect_asset_shape_operator_to_asset_operator function for "{}" is not implemented!'.format(
                self.__class__.__name__))

    @decorators.abstractmethod
    def add_asset_shape_operator_assignment(self, asset_id, asset_shape, value):
        """
        Sets assignment of the given asset shape operator
        :param asset_id: str
        :param asset_shape: str
        :param value: str
        :return: bool
        """

        raise NotImplementedError(
            'add_asset_shape_operator_assignment function for "{}" is not implemented!'.format(
                self.__class__.__name__))

    @decorators.abstractmethod
    def remove_asset_shape_operator_assignment(self, asset_id, asset_shape, value):
        """
        Removes assignment of the given asset shape operator
        :param asset_id: str
        :param asset_shape: str
        :param value: str
        :return: bool
        """

        raise NotImplementedError(
            'remove_asset_shape_operator_assignment function for "{}" is not implemented!'.format(
                self.__class__.__name__))

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
