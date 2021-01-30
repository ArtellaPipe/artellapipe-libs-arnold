#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains utilities functions to work with Arnold in Maya
"""

from __future__ import print_function, division, absolute_import

import os
import logging

from tpDcc import dcc
from tpDcc.managers import configs
from tpDcc.dccs.maya.core import standin, attribute as attr_utils

from artellapipe.utils import exceptions
from artellapipe.managers import files

from artellapipe.libs.arnold.core import consts

logger = logging.getLogger(consts.LIB_ID)


def load_arnold_plugin():
    """
    Forces the loading of the Alembic plugin if it is not already loaded
    """

    if not dcc.client().is_plugin_loaded('mtoa.mll'):
        dcc.client().load_plugin('mtoa.mll')


def is_arnold_usd_available():
    """
    Returns whether or not Arnold USD libraries and schemas are available in current session
    :return: bool
    """

    try:
        import UsdArnold
    except Exception:
        return False

    return True


def load_arnold_usd_plugin():
    """
    Forces the loading of the Arnold USD plugin if it is not already loaded
    """

    pass


def get_asset_operator(asset_id, connect_to_scene_operator=True, create=True):
    """
    Creates asset operator node with the given name
    :param asset_id: str
    :param connect_to_scene_operator: bool
    :return: str
    """

    asset_operator = None
    merge_nodes = dcc.client().list_nodes(node_type='aiMerge') or list()
    for merge_node in merge_nodes:
        if dcc.client().attribute_exists(merge_node, 'asset_id'):
            asset_id_value = dcc.client().get_attribute_value(merge_node, 'asset_id')
            if asset_id_value == asset_id:
                asset_operator = merge_node
                break
    if asset_operator:
        return asset_operator

    if not create:
        return None

    asset_operator_name = '{}_operator'.format(asset_id)
    if dcc.node_exists(asset_operator_name):
        return asset_operator_name

    asset_operator_node = dcc.client().create_node('aiMerge', node_name=asset_operator_name)
    dcc.client().add_string_attribute(asset_operator_node, 'asset_id')
    dcc.client().set_string_attribute_value(asset_operator_node, 'asset_id', asset_id)
    if connect_to_scene_operator:
        connect_asset_operator_to_scene_operator(asset_operator_node)

    return asset_operator_node


def get_asset_shape_operator(asset_id, asset_shape=None, connect_to_asset_operator=True, create=True):
    """
    Creates asset shape operator node with the given name
    :param asset_id: str
    :param asset_shape: str
    :param connect_to_asset_operator: bool
    :param create: bool
    :return: str or None
    """

    asset_shape_operator = None
    set_nodes = dcc.client().list_nodes(node_type='aiSetParameter') or list()
    for set_node in set_nodes:
        if asset_shape:
            if dcc.client().attribute_exists(set_node, 'asset_shape'):
                asset_shape_value = dcc.client().get_attribute_value(set_node, 'asset_shape')
                if asset_shape_value == asset_shape:
                    asset_shape_operator = set_node
                    break
        else:
            asset_id_value = None
            asset_shape_value = None
            if dcc.client().attribute_exists(set_node, 'asset_id'):
                asset_id_value = dcc.client().get_attribute_value(set_node, 'asset_id')
            if dcc.client().attribute_exists(set_node, 'asset_shape'):
                asset_shape_value = dcc.client().get_attribute_value(set_node, 'asset_shape')
            if asset_id_value == asset_id and (not asset_shape_value or asset_shape_value == 'None'):
                asset_shape_operator = set_node
                break

    if asset_shape_operator:
        return asset_shape_operator

    if not create:
        return None

    if asset_shape:
        shape_name = asset_shape.split(':')[-1]
        asset_shape_node_name = '{}_{}_set'.format(asset_id, shape_name)
    else:
        shape_name = ''
        asset_shape_node_name = '{}_set'.format(asset_id)

    if dcc.node_exists(asset_shape_node_name):
        return asset_shape_node_name

    asset_shape_operator = dcc.client().create_node('aiSetParameter', node_name=asset_shape_node_name)
    dcc.client().set_string_attribute_value(asset_shape_operator, 'selection', '{}:*{}'.format(asset_id, shape_name))
    dcc.client().add_string_attribute(asset_shape_operator, 'asset_id')
    dcc.client().add_string_attribute(asset_shape_operator, 'asset_shape')
    dcc.client().set_string_attribute_value(asset_shape_operator, 'asset_id', asset_id)
    dcc.client().set_string_attribute_value(asset_shape_operator, 'asset_shape', asset_shape)
    if connect_to_asset_operator:
        connect_asset_shape_operator_to_asset_operator(asset_shape_operator)

    return asset_shape_operator


def get_scene_operator(create=True):
    """
    Returns Arnold scene operator node. The node is created if it does already exists
    :return: str
    """

    scene_operator = configs.get_library_config(consts.LIB_ID).get('assets_operator_name', default='assets_operator')
    if create:
        if not dcc.node_exists(scene_operator):
            scene_operator = dcc.client().create_node('aiMerge', node_name='assets_operator')
    try:
        dcc.client().connect_attribute(scene_operator, 'message', 'defaultArnoldRenderOptions', 'operator', force=True)
    except Exception:
        pass

    return scene_operator


def remove_scene_operator():
    """
    Removes scene shader operator node if it has no more connections
    """

    scene_operator = get_scene_operator(create=False)
    if not scene_operator or not dcc.node_exists(scene_operator):
        return

    inputs = dcc.client().list_source_connections(scene_operator)
    if inputs:
        logger.warning(
            'Impossible to remove scene operator: "{}" because it has input connections!'.format(scene_operator))
        return

    dcc.client().delete_object(scene_operator)

    return True


def connect_asset_operator_to_scene_operator(asset_operator_name):
    """
    Connects given asset operator node to the scene operator node
    :param asset_operator_name: str
    :return: bool
    """

    if not asset_operator_name or not dcc.node_exists(asset_operator_name):
        return
    scene_operator = get_scene_operator()
    next_asset_index = attr_utils.next_available_multi_index(
        '{}.inputs'.format(scene_operator), use_connected_only=False)
    dcc.client().connect_attribute(
        source_node=asset_operator_name, source_attribute='out',
        target_node=scene_operator, target_attribute='inputs[{}]'.format(next_asset_index)
    )

    return True


def connect_asset_shape_operator_to_asset_operator(asset_shape_operator_name):
    """
    Connects given asset shape operator node to the asset operator node
    :param asset_shape_operator_name: str
    :return: bool
    """

    if not asset_shape_operator_name or not dcc.node_exists(asset_shape_operator_name):
        return
    if not dcc.client().attribute_exists(asset_shape_operator_name, 'asset_id'):
        return
    asset_id = dcc.client().get_attribute_value(asset_shape_operator_name, 'asset_id')
    asset_operator = get_asset_operator(asset_id)
    if not asset_operator:
        logger.warning(
            'Impossible to connect shape operator "{}" because asset operator does not exist!'.format(
                asset_shape_operator_name))
        return
    next_asset_index = attr_utils.next_available_multi_index(
        '{}.inputs'.format(asset_operator), use_connected_only=False)
    dcc.client().connect_attribute(
        source_node=asset_shape_operator_name, source_attribute='out',
        target_node=asset_operator, target_attribute='inputs[{}]'.format(next_asset_index))


def add_asset_shape_operator_assignment(asset_id, asset_shape, value):
    """
    Sets assignment of the given asset shape operator
    :param asset_id: str
    :param asset_shape: str
    :param value: str
    :return: bool
    """

    asset_shape_operator = get_asset_shape_operator(asset_id, asset_shape, create=False)
    if not asset_shape_operator or not dcc.node_exists(asset_shape_operator):
        return False

    value_found = False
    existing_assignments = attr_utils.multi_index_list('{}.assignment'.format(asset_shape_operator))
    for i in range(len(existing_assignments)):
        assign_value = dcc.client().get_attribute_value(asset_shape_operator, 'assignment[{}]'.format(i))
        if assign_value == value:
            value_found = True
            break

    if value_found:
        logger.warning('Asset Shape Operator Assignment "{} | {}" already set!'.format(asset_shape_operator, value))
        return False

    next_asset_index = None
    multi_index = attr_utils.multi_index_list('{}.assignment'.format(asset_shape_operator))
    for i in range(len(multi_index)):
        index_attr_value = dcc.client().get_attribute_value(asset_shape_operator, 'assignment[{}]'.format(i))
        if not index_attr_value:
            next_asset_index = i

    if next_asset_index is None:
        next_asset_index = attr_utils.next_available_multi_index(
            '{}.assignment'.format(asset_shape_operator), use_connected_only=False)

    dcc.client().set_string_attribute_value(asset_shape_operator, 'assignment[{}]'.format(next_asset_index), value)

    return True


def remove_asset_shape_operator_assignment(asset_id, asset_shape, value):
    """
    Removes assignment of the given asset shape operator
    :param asset_id: str
    :param asset_shape: str
    :param value: str
    :return: bool
    """

    asset_shape_operator = get_asset_shape_operator(asset_id, asset_shape, create=False)
    if not asset_shape_operator or not dcc.node_exists(asset_shape_operator):
        return False

    value_removed = False
    existing_assignments = attr_utils.multi_index_list('{}.assignment'.format(asset_shape_operator))
    for i in range(len(existing_assignments)):
        assign_value = dcc.client().get_attribute_value(asset_shape_operator, 'assignment[{}]'.format(i))
        if assign_value.startswith(value):
            dcc.client().set_string_attribute_value(asset_shape_operator, 'assignment[{}]'.format(i), '')
            value_removed = True
            break

    return value_removed


def import_standin(
        standin_file, mode='import', nodes=None, parent=None, fix_path=False,
        namespace=None, reference=False, unique_namespace=True):
    """
    Imports Standin into current DCC scene

    :param str standin_file: file we want to load
    :param str mode: mode we want to use to import the Alembic File
    :param list(str) nodes: optional list of nodes to import
    :param parent:
    :param fix_path: bool, whether to fix path or not
    :param namespace: str
    :param reference: bool
    :param unique_namespace: bool
    :return:
    """

    if not os.path.exists(standin_file):
        logger.error('Given Standin File: {} does not exists!'.format(standin_file))
        dcc.client().confirm_dialog(
            title='Error',
            message='Standin File does not exists:\n{}'.format(standin_file)
        )
        return None

    # Make sure Alembic plugin is loaded
    load_arnold_plugin()

    logger.debug(
        'Import Standin File (%s) with job arguments:\n\t(standin_file) %s\n\t(nodes) %s', mode,
        standin_file, nodes)

    res = None
    try:
        if fix_path:
            ass_file = files.fix_path(standin_file)
        else:
            ass_file = standin_file

        if not reference:
            res = standin.import_standin(ass_file, namespace=namespace, unique_namespace=unique_namespace)
        else:
            if reference:
                if namespace:
                    res = dcc.client().reference_file(ass_file, namespace=namespace, unique_namespace=unique_namespace)
                else:
                    res = dcc.client().reference_file(ass_file)
    except RuntimeError as exc:
        exceptions.capture_sentry_exception(exc)
        return res

    if reference:
        logger.info('Standin File %s referenced successfully!', os.path.basename(ass_file))
    else:
        logger.info('Standin File %s imported successfully!', os.path.basename(ass_file))

    return res


def export_usd(
        file_directory, file_name, extension=None, export_shapes=True, export_shaders=True, export_selection=False):

    import maya.cmds
    from artellapipe.libs.usd.core import usdutils, usdcat

    extension = extension or usdutils.UsdFormats.Text

    if not is_arnold_usd_available():
        logger.warning('Impossible to export Arnold USD file. Arnold USD is not available!')
        return False

    if not extension.startswith('.'):
        extension = '.{}'.format(extension)

    full_file_name = '{}{}'.format(file_name, extension)
    file_path = os.path.join(file_directory, full_file_name)

    out_file = maya.cmds.file(
        file_path, force=True, options='-shadowLinks 0;-mask 8;-lightLinks 0;-boundingBox;-asciiAss',
        typ='Arnold-USD', pr=True, ea=not export_selection, es=export_selection)
    if not out_file:
        logger.error('Something went wrong while exporting Arnold USD file')
        return False

    out_ext = os.path.splitext(os.path.basename(out_file))[-1]
    if out_ext == usdutils.UsdFormats.Generic:
        if extension == usdutils.UsdFormats.Text:
            valid_conversion = usdcat.convert_usd_file(out_file, extension, clean_original=False)
            if not valid_conversion:
                logger.error('Something went wrong while convert USD file: {} > {}'.format(out_ext, extension))
                return False

    return True
