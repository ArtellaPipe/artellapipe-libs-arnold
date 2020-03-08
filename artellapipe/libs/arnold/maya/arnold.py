#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains utilities functions to work with Arnold in Maya
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

import os
import logging

import tpDcc as tp
from tpDcc.libs.python import decorators

import tpDcc.dccs.maya as maya
from tpDcc.dccs.maya.core import standin, attribute as attr_utils

import artellapipe.register
from artellapipe.utils import exceptions
from artellapipe.libs import arnold as arnold_lib
from artellapipe.libs.arnold.core import arnold

LOGGER = logging.getLogger()


class MayaArnold(arnold.AbstractArnold):

    def load_arnold_plugin(self):
        """
        Forces the loading of the Alembic plugin if it is not already loaded
        """

        if not tp.Dcc.is_plugin_loaded('mtoa.mll'):
            tp.Dcc.load_plugin('mtoa.mll')

    def get_asset_operator(self, asset_id, connect_to_scene_operator=True, create=True):
        """
        Creates asset operator node with the given name
        :param asset_id: str
        :param connect_to_scene_operator: bool
        :return: str
        """

        asset_operator = None
        merge_nodes = tp.Dcc.list_nodes(node_type='aiMerge') or list()
        for merge_node in merge_nodes:
            if tp.Dcc.attribute_exists(merge_node, 'asset_id'):
                asset_id_value = tp.Dcc.get_attribute_value(merge_node, 'asset_id')
                if asset_id_value == asset_id:
                    asset_operator = merge_node
                    break
        if asset_operator:
            return asset_operator

        if not create:
            return None

        asset_operator_name = '{}_operator'.format(asset_id)
        if tp.Dcc.object_exists(asset_operator_name):
            return asset_operator_name

        asset_operator_node = maya.cmds.createNode('aiMerge', name=asset_operator_name)
        tp.Dcc.add_string_attribute(asset_operator_node, 'asset_id')
        tp.Dcc.set_string_attribute_value(asset_operator_node, 'asset_id', asset_id)
        if connect_to_scene_operator:
            self.connect_asset_operator_to_scene_operator(asset_operator_node)

        return asset_operator_node

    def get_asset_shape_operator(self, asset_id, asset_shape=None, connect_to_asset_operator=True, create=True):
        """
        Creates asset shape operator node with the given name
        :param asset_id: str
        :param asset_shape: str
        :param connect_to_asset_operator: bool
        :param create: bool
        :return: str or None
        """

        asset_shape_operator = None
        set_nodes = tp.Dcc.list_nodes(node_type='aiSetParameter') or list()
        for set_node in set_nodes:
            if asset_shape:
                if tp.Dcc.attribute_exists(set_node, 'asset_shape'):
                    asset_shape_value = tp.Dcc.get_attribute_value(set_node, 'asset_shape')
                    if asset_shape_value == asset_shape:
                        asset_shape_operator = set_node
                        break
            else:
                asset_id_value = None
                asset_shape_value = None
                if tp.Dcc.attribute_exists(set_node, 'asset_id'):
                    asset_id_value = tp.Dcc.get_attribute_value(set_node, 'asset_id')
                if tp.Dcc.attribute_exists(set_node, 'asset_shape'):
                    asset_shape_value = tp.Dcc.get_attribute_value(set_node, 'asset_shape')
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

        if tp.Dcc.object_exists(asset_shape_node_name):
            return asset_shape_node_name

        asset_shape_operator = maya.cmds.createNode('aiSetParameter', name=asset_shape_node_name)
        tp.Dcc.set_string_attribute_value(asset_shape_operator, 'selection', '{}:*{}'.format(asset_id, shape_name))
        tp.Dcc.add_string_attribute(asset_shape_operator, 'asset_id')
        tp.Dcc.add_string_attribute(asset_shape_operator, 'asset_shape')
        tp.Dcc.set_string_attribute_value(asset_shape_operator, 'asset_id', asset_id)
        tp.Dcc.set_string_attribute_value(asset_shape_operator, 'asset_shape', asset_shape)
        if connect_to_asset_operator:
            self.connect_asset_shape_operator_to_asset_operator(asset_shape_operator)

        return asset_shape_operator

    def get_scene_operator(self, create=True):
        """
        Returns Arnold scene operator node. The node is created if it does already exists
        :return: str
        """

        scene_operator = arnold_lib.config.get('assets_operator_name', default='assets_operator')
        if create:
            if not tp.Dcc.object_exists(scene_operator):
                scene_operator = maya.cmds.createNode('aiMerge', name='assets_operator')
        try:
            tp.Dcc.connect_attribute(scene_operator, 'message', 'defaultArnoldRenderOptions', 'operator', force=True)
        except Exception:
            pass

        return scene_operator

    def remove_scene_operator(self):
        """
        Removes scene shader operator node if it has no more connections
        """

        scene_operator = self.get_scene_operator(create=False)
        if not scene_operator or not tp.Dcc.object_exists(scene_operator):
            return

        inputs = tp.Dcc.list_source_connections(scene_operator)
        if inputs:
            LOGGER.warning(
                'Impossible to remove scene operator: "{}" because it has input connections!'.format(scene_operator))
            return

        tp.Dcc.delete_object(scene_operator)

        return True

    def connect_asset_operator_to_scene_operator(self, asset_operator_name):
        """
        Connects given asset operator node to the scene operator node
        :param asset_operator_name: str
        :return: bool
        """

        if not asset_operator_name or not tp.Dcc.object_exists(asset_operator_name):
            return
        scene_operator = self.get_scene_operator()
        next_asset_index = attr_utils.next_available_multi_index(
            '{}.inputs'.format(scene_operator), use_connected_only=False)
        tp.Dcc.connect_attribute(
            source_node=asset_operator_name, source_attribute='out',
            target_node=scene_operator, target_attribute='inputs[{}]'.format(next_asset_index)
        )

        return True

    def connect_asset_shape_operator_to_asset_operator(self, asset_shape_operator_name):
        """
        Connects given asset shape operator node to the asset operator node
        :param asset_shape_operator_name: str
        :return: bool
        """

        if not asset_shape_operator_name or not tp.Dcc.object_exists(asset_shape_operator_name):
            return
        if not tp.Dcc.attribute_exists(asset_shape_operator_name, 'asset_id'):
            return
        asset_id = tp.Dcc.get_attribute_value(asset_shape_operator_name, 'asset_id')
        asset_operator = self.get_asset_operator(asset_id)
        if not asset_operator:
            LOGGER.warning(
                'Impossible to connect shape operator "{}" because asset operator does not exist!'.format(
                    asset_shape_operator_name))
            return
        next_asset_index = attr_utils.next_available_multi_index(
            '{}.inputs'.format(asset_operator), use_connected_only=False)
        tp.Dcc.connect_attribute(
            source_node=asset_shape_operator_name, source_attribute='out',
            target_node=asset_operator, target_attribute='inputs[{}]'.format(next_asset_index))

    def add_asset_shape_operator_assignment(self, asset_id, asset_shape, value):
        """
        Sets assignment of the given asset shape operator
        :param asset_id: str
        :param asset_shape: str
        :param value: str
        :return: bool
        """

        asset_shape_operator = self.get_asset_shape_operator(asset_id, asset_shape, create=False)
        if not asset_shape_operator or not tp.Dcc.object_exists(asset_shape_operator):
            return False

        value_found = False
        existing_assignments = attr_utils.multi_index_list('{}.assignment'.format(asset_shape_operator))
        for i in range(len(existing_assignments)):
            assign_value = tp.Dcc.get_attribute_value(asset_shape_operator, 'assignment[{}]'.format(i))
            if assign_value == value:
                value_found = True
                break

        if value_found:
            LOGGER.warning('Asset Shape Operator Assignment "{} | {}" already set!'.format(asset_shape_operator, value))
            return False

        next_asset_index = None
        multi_index = attr_utils.multi_index_list('{}.assignment'.format(asset_shape_operator))
        for i in range(len(multi_index)):
            index_attr_value = tp.Dcc.get_attribute_value(asset_shape_operator, 'assignment[{}]'.format(i))
            if not index_attr_value:
                next_asset_index = i

        if next_asset_index is None:
            next_asset_index = attr_utils.next_available_multi_index(
                '{}.assignment'.format(asset_shape_operator), use_connected_only=False)

        tp.Dcc.set_string_attribute_value(asset_shape_operator, 'assignment[{}]'.format(next_asset_index), value)

        return True

    def remove_asset_shape_operator_assignment(self, asset_id, asset_shape, value):
        """
        Removes assignment of the given asset shape operator
        :param asset_id: str
        :param asset_shape: str
        :param value: str
        :return: bool
        """

        asset_shape_operator = self.get_asset_shape_operator(asset_id, asset_shape, create=False)
        if not asset_shape_operator or not tp.Dcc.object_exists(asset_shape_operator):
            return False

        value_removed = False
        existing_assignments = attr_utils.multi_index_list('{}.assignment'.format(asset_shape_operator))
        for i in range(len(existing_assignments)):
            assign_value = tp.Dcc.get_attribute_value(asset_shape_operator, 'assignment[{}]'.format(i))
            if assign_value.startswith(value):
                tp.Dcc.set_string_attribute_value(asset_shape_operator, 'assignment[{}]'.format(i), '')
                value_removed = True
                break

        return value_removed

    def import_standin(self, standin_file, mode='import', nodes=None, parent=None, fix_path=False,
                       namespace=None, reference=False, unique_namespace=True):
        """
        Imports Standin into current DCC scene

        :param ArtellaProject project: Project this Standin will belong to
        :param str alembic_file: file we want to load
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
            LOGGER.error('Given Standin File: {} does not exists!'.format(standin_file))
            tp.Dcc.confirm_dialog(
                title='Error',
                message='Standin File does not exists:\n{}'.format(standin_file)
            )
            return None

        # Make sure Alembic plugin is loaded
        self.load_arnold_plugin()

        LOGGER.debug(
            'Import Standin File (%s) with job arguments:\n\t(standin_file) %s\n\t(nodes) %s', mode,
            standin_file, nodes)

        res = None
        try:
            if fix_path:
                ass_file = artellapipe.FilesMgr().fix_path(standin_file)
            else:
                ass_file = standin_file

            if not reference:
                res = standin.import_standin(ass_file, namespace=namespace, unique_namespace=unique_namespace)
            else:
                if reference:
                    if namespace:
                        res = tp.Dcc.reference_file(ass_file, namespace=namespace, unique_namespace=unique_namespace)
                    else:
                        res = tp.Dcc.reference_file(ass_file)
        except RuntimeError as exc:
            exceptions.capture_sentry_exception(exc)
            return res

        if reference:
            LOGGER.info('Standin File %s referenced successfully!', os.path.basename(ass_file))
        else:
            LOGGER.info('Standin File %s imported successfully!', os.path.basename(ass_file))

        return res


@decorators.Singleton
class MayaArnoldSingleton(MayaArnold, object):
    def __init__(self):
        MayaArnold.__init__(self)


artellapipe.register.register_class('Arnold', MayaArnoldSingleton)
