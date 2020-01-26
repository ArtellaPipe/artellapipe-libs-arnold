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

import tpDccLib as tp
from tpPyUtils import decorators

if tp.is_maya():
    from tpMayaLib.core import standin

import artellapipe.register
from artellapipe.utils import exceptions
from artellapipe.libs.arnold.core import arnold

LOGGER = logging.getLogger()


class MayaArnold(arnold.AbstractArnold):

    def load_arnold_plugin(self):
        """
        Forces the loading of the Alembic plugin if it is not already loaded
        """

        if not tp.Dcc.is_plugin_loaded('mtoa.mll'):
            tp.Dcc.load_plugin('mtoa.mll')

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
