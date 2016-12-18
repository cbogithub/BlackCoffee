#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Created on 12/17/16 11:00 PM

@author: imyin

@File: mail_quota
"""
import os
import sys

CONSTANTS_PATH = os.path.dirname(os.getcwd())
sys.path.append(CONSTANTS_PATH)
import Constants as cons

QUOTA_PATH=cons.ANALYSIS_PATH
sys.path.append(QUOTA_PATH)
import quota_analysis as qa

