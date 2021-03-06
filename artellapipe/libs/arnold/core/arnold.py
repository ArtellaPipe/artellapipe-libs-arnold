#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains utilities functions to work with Arnold
"""

from __future__ import print_function, division, absolute_import

from tpDcc.core import dcc as core_dcc
from tpDcc.core import library, reroute

from artellapipe.libs.arnold.core import consts


class ArnodlLib(library.DccLibrary, object):

    ID = consts.LIB_ID

    def __init__(self, *args, **kwargs):
        super(ArnodlLib, self).__init__(*args, **kwargs)

    @classmethod
    def config_dict(cls):
        base_tool_config = library.DccLibrary.config_dict()
        tool_config = {
            'name': 'Arnold Library',
            'id': ArnodlLib.ID,
            'supported_dccs': {
                core_dcc.Dccs.Maya: ['2017', '2018', '2019', '2020'],
                core_dcc.Dccs.Houdini: ['18.0.391']
            },
            'tooltip': 'Library to handle Alembics',
            'root': cls.ROOT if hasattr(cls, 'ROOT') else '',
            'file': cls.PATH if hasattr(cls, 'PATH') else '',
        }
        base_tool_config.update(tool_config)

        return base_tool_config


@reroute.reroute_factory(ArnodlLib.ID, 'arnold')
def load_arnold_plugin():
    """
    Forces the loading of the Arnold plugin if it is not already loaded
    """

    raise NotImplementedError('load_arnold_plugin function is not implemented!')


@reroute.reroute_factory(ArnodlLib.ID, 'arnold')
def is_arnold_usd_available():
    """
    Returns whether or not Arnold USD libraries and schemas are available in current session
    :return: bool
    """

    raise NotImplementedError('is_arnold_usd_available function is not implemented!')


@reroute.reroute_factory(ArnodlLib.ID, 'arnold')
def get_asset_operator(asset_id, connect_to_scene_operator=True, create=True):
    """
    Creates asset operator node with the given name
    :param asset_id: str
    :param connect_to_scene_operator: bool
    :param create: bool
    :return: str or None
    """

    raise NotImplementedError('get_asset_operator function is not implemented!')


@reroute.reroute_factory(ArnodlLib.ID, 'arnold')
def get_asset_shape_operator(asset_id, asset_shape, connect_to_asset_operator=True, create=True):
    """
    Creates asset shape operator node with the given name
    :param asset_id: str
    :param asset_shape: str
    :param connect_to_asset_operator: bool
    :param create: bool
    :return: str or None
    """

    raise NotImplementedError('get_asset_shape_operator function is not implemented!')


@reroute.reroute_factory(ArnodlLib.ID, 'arnold')
def get_scene_operator():
    """
    Returns Arnold scene operator node. The node is created if it does already exists
    :return:
    """

    raise NotImplementedError('get_scene_operator function is not implemented!')


@reroute.reroute_factory(ArnodlLib.ID, 'arnold')
def remove_scene_operator():
    """
    Removes Arnold scene operator node if exists
    :return:
    """

    raise NotImplementedError('remove_scene_operator function is not implemented!')


@reroute.reroute_factory(ArnodlLib.ID, 'arnold')
def connect_asset_operator_to_scene_operator(asset_operator_name):
    """
    Connects given asset operator node to the scene operator node
    :param asset_operator_name: str
    :return: bool
    """

    raise NotImplementedError('connect_asset_operator_to_scene_operator function is not implemented!')


@reroute.reroute_factory(ArnodlLib.ID, 'arnold')
def connect_asset_shape_operator_to_asset_operator(asset_shape_operator_name):
    """
    Connects given asset shape operator node to the asset operator node
    :param asset_shape_operator_name: str
    :return: bool
    """

    raise NotImplementedError('connect_asset_shape_operator_to_asset_operator function is not implemented!')


@reroute.reroute_factory(ArnodlLib.ID, 'arnold')
def add_asset_shape_operator_assignment(asset_id, asset_shape, value):
    """
    Sets assignment of the given asset shape operator
    :param asset_id: str
    :param asset_shape: str
    :param value: str
    :return: bool
    """

    raise NotImplementedError('add_asset_shape_operator_assignment function is not implemented!')


@reroute.reroute_factory(ArnodlLib.ID, 'arnold')
def remove_asset_shape_operator_assignment(asset_id, asset_shape, value):
    """
    Removes assignment of the given asset shape operator
    :param asset_id: str
    :param asset_shape: str
    :param value: str
    :return: bool
    """

    raise NotImplementedError('remove_asset_shape_operator_assignment function is not implemented!')


@reroute.reroute_factory(ArnodlLib.ID, 'arnold')
def export_standin(self, *args, **kwargs):
    """
    Exports Standin file with given attributes
    """

    raise NotImplementedError('export_standin function is not implemented!')


@reroute.reroute_factory(ArnodlLib.ID, 'arnold')
def import_standin(
        standin_file, mode='import', nodes=None, parent=None, fix_path=False, namespace=None, reference=False, **kwargs):
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

    raise NotImplementedError('import_standin function is not implemented!')


@reroute.reroute_factory(ArnodlLib.ID, 'arnold')
def export_usd(
        file_directory, file_name, extension=None,
        export_shapes=True, export_shaders=True, export_selection=False):

    raise NotImplementedError('export_usd function is not implemented!')
