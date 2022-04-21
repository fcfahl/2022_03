import os
import logging
import yaml
import grass.script as grass
import grass.script.setup as gsetup
import models.utils.paths as pth

class GrassConfig:

    path  = pth.PathDefinition()

    def __init__(self):
        self.checkGrassRunning()

    def checkGrassRunning(self):

        self.grassdb = dict(
            gisbase=  '/usr/local/bin/grass',
            mapset= 'PERMANENT',
            gisdb = self.path.grass,
            location = self.path.project_name,
        )

        if "GRASS_VERSION" not in os.environ:
            gsetup.init(self.grassdb['gisbase'],self.grassdb['gisdb'],self.grassdb['location'],self.grassdb['mapset'])
            print('GRASS TERMINAL SESSION')
            return False
        else:
            print('GRASS NATIVE SESSION')
            return True


    # ____________________ print attributes
    def __str__(self):
        return  '\n'.join((f'\n____________ {key} ____________\n{value}' for key, value in self.__dict__.items()))

