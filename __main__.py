#!/usr/bin/python
# -*- coding: utf-8 -*-
""" .....
"""

__author__ = "Fernando Fahl <fernando.fahl@gmail.com>"
__version__ = "1.0"
__date__ = "April 2022"

import controller as ctr
import data.loader as ldr
import data.crop_calculations as crp

if __name__ == "__main__":

    # _______________ objects
    obj = ctr.Controller()

    ldr.import_vectors(obj)
    ldr.import_rasters(obj)




    # print (obj)
