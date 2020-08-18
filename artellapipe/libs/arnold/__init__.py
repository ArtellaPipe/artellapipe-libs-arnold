#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Initialization module for artellapipe-libs-arnold
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

import tpDcc as tp

import artellapipe.register


def init(*args, **kwargs):

    from artellapipe.libs.arnold.core import arnold
    artellapipe.register.register_class('Arnold', arnold.AbstractArnold)

    if tp.is_maya():
        from artellapipe.libs.arnold.maya import arnold as maya_arnold
        artellapipe.register.register_class('Arnold', maya_arnold.MayaArnold)
