# -*- coding: utf-8 -*-

import yaml
from .utils import *
import logging


default_config = {
    # Where to run
    "port": "6543",
    "interface": "0.0.0.0",

    # Target system
    "endpoint": "http://localhost:9001/api/sinks/test-sink/entities",   # SDShare Push Receiver

    # Default graph, empty means post back to same graph as we get in the request
    "graph": "",

    # Coordinate systems
    "sourceCoordinateSystem": "EPSG:32632",  # UTM zone 32N
    "targetCoordinateSystem": "EPSG:4326",   # WGS84
    "switch_x_y": False,                     # Whether the input-coords are (x,y) or (y,x)
    "switch_x_y_out": False,                 # Whether the output-coords are (x,y) or (y,x)

    # Source predicates
    "sourceGeometry": "https://example.com/etrs89",

    # Target predicates
    "targetGeometry": "http://example.com/wgs84_pos#lat_long",
    "targetDatatype": "http://www.openlinksw.com/schemas/virtrdf#Geometry",

    # Default logfile/level from the options dict
    "logfile": "wktprojectionservice.log",
    "loglevel": logging.INFO
}


def read_config(configfile, port=None, interface=None, logfile=None, loglevel=None, env=None, logger=None):
    """ Read a config file or return a default config """
    global default_config

    merged_config = default_config.copy()
    
    if not env:
        env = os.environ.copy()

    config_file = configfile.strip()
    if not os.path.isabs(config_file):
        root_folder = getCurrDir()
        config_file = os.path.join(root_folder, config_file)

    if logger:
        logger.debug("Reading config file from '%s'..." % config_file)

    if os.path.isfile(config_file):
        stream = open(config_file, 'r')
        config = yaml.load(stream)
        stream.close()
    else:
        config = {}
        msg = "Could not find config file '%s'. Using defaults." % config_file
        if logger:
            logger.warning(msg)
        
    merged_config.update(config)

    if merged_config["logfile"] is not None and not os.path.isabs(merged_config["logfile"]):
        log_folder = getCurrDir()
        assertDir(log_folder)
        merged_config["logfile"] = os.path.join(log_folder, merged_config["logfile"])

    if not merged_config["loglevel"]:
        merged_config["loglevel"] = loglevel
 
    # Override config with command line parameters if any
    if port:
        merged_config["port"] = port

    if interface:
        merged_config["interface"] = port

    return merged_config

