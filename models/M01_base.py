import os, wrapt, logging, pathlib
from datetime import datetime, timedelta


import models.utils.grass_config as cnf
import models.utils.logs as log
import models.utils.paths as pth
import models.utils.utilities as utl


class Base(log.Logger):

    def __init__(self):

        path            = self.get_path() # not used self to avoid multiple definitions of same parameter
        utls             = self.get_utl()

        self.params     = self.get_yaml_parameters(path, utls)
        self.quiet      = self.get_verbose_status()
        self.crop_names = self.get_crop_names()
        self.resolution = self.get_resolution()
        self.reference_year = self.get_reference_year()

        # cnf.GrassConfig()

    ################## UTILITIES

    def get_path(self):
        return pth.PathDefinition()

    def get_utl(self):
        return utl

    def get_logger(self, path, utls):
        return log.Logger(path, utls)

    ################## YAML LOAD

    def get_yaml_parameters(self, path, utls):
        return utls.load_yaml(path.config.joinpath('parameters.yaml'))

    ################## PARAMETERS

    def get_crop_names(self):
        return list(self.params.get('crop_names').keys())

    def get_resolution(self):
        return self.params.get('resolution').get('value')

    def get_reference_year(self):
        return self.params.get('reference').get('year')

    def get_validation_coordinates(self):
        return self.params.get('validation')

    def get_bbox(self, latlon=False):
        if latlon:
            return self.params.get('bbox_4326')
        else:
            return self.params.get('bbox_3035')

    ################## ATTRIBUTES

    def set_attribute(self, attr, value, at=False, dict_=True):
        setattr(self, attr, value)
        if at:
            if dict:
                setattr(self, f"{attr}_at", {key: f"{layer}@{self.mapset}" for key, layer in value.items()})
            else:
                setattr(self, f"{attr}_at", f"{value}@{self.mapset}")

    def get_obj_attribute(self, attr, at=False):

        if at:
            return getattr(self, f"{attr}_at")
        else:
            return getattr(self, attr)

    ################## LAYERS

    def set_mask_attr(self, mask):
        self.mask = mask

    ############# GENERAL

    def get_verbose_status(self):
        return self.params['verbose']['quiet']

    def return_dict(self, params, dict_=True):

        if dict:
            return params
        else:
            return list(params.values())

    # ____________________ print attributes
    def __str__(self):
        return '\n:'.join((f'{key:<20s} = {value}' for key, value in self.__dict__.items() if key not in ['log', 'params', 'quiet']))
        # return  '\n'.join((f'\n____________ {key} ____________\n{value}' for key, value in self.__dict__.items()))

