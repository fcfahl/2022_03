
import logging
import logging.config
import yaml

class Logger():

    def __init__(self, path, utl):
        self.log = None
        self.path = path
        self.utl = utl
        self.setup_logger()

    def reset_logs(self):
        self.utl.delete_files_by_extension(self.path.log, 'log')

    def setup_logger(self):

        with open(self.path.config.joinpath('log_config.yaml'), 'r') as f:
            log_cfg = yaml.safe_load(f.read())

        logging.config.dictConfig(log_cfg)
        # #
        # self.log = logging.getLogger('a')
        # self.log.setLevel(logging.DEBUG)
        #
        # self.info('___ Initiate log ___')
        # self.warning('___ Initiate log ___')
        # self.debug('___ Initiate log ___')
        # self.error('___ Initiate log ___')
        # self.critical('___ Initiate log ___')
        self.grass_log('___ GRASS Initiate log ___')


    def info(self, msg=None):
        log = logging.getLogger('a')
        log.info(msg)

    def warning(self, msg):
        log = logging.getLogger('b')
        log.warning(msg)

    def debug(self, msg):
        log = logging.getLogger('c')
        log.debug(msg)

    def error(self, msg):
        log = logging.getLogger('c')
        log.error(msg)

    def critical(self, msg):
        log = logging.getLogger('c')
        log.critical(msg)

    def grass_log(self, msg):
        log = logging.getLogger('g')
        log.debug(msg)


    def __str__(self):
        return '\n'.join(('{:<20s} = {}'.format(item, self.__dict__[item]) for item in self.__dict__))



#
# class Logger():
#
#     def __init__(self):
#         pass
#         # self.log = self.setup_logger()
#         # self.info(self.log)
#     #
#     #
#     def setup_logger(self):
#
#         path = pth.PathDefinition().log
#         log_filename = 'info.log'
#         log_filepath = path.joinpath(log_filename)
#
#         formatter = logging.Formatter('%(filename)s: %(message)s')
#
#         # formatter = logging.Formatter('%(asctime)s | %(levelname)s \t\t| %(message)s', "%H:%M:%S")
#
#         handler = logging.FileHandler(log_filepath, 'w+')
#         handler.setFormatter(formatter)
#
#         logger = logging.getLogger(log_filename)
#         logger.setLevel(logging.CRITICAL)
#         logger.addHandler(handler)
#
#         self.log = logger
#         logging.debug('This is a debug message')
#
#         self.log.info('test')
#
#         return self.log


