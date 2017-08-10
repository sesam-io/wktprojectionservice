# -*- coding: utf-8 -*-


from wsgiref.simple_server import make_server
from pyramid.response import Response
from pyramid.view import view_config
import argparse
import sys
import traceback
import logging
from wktprojectionservice.config import *
from wktprojectionservice.convert import *


logger = None
config = None


@view_config(route_name='form', request_method='GET', renderer='templates/form.pt')
def form(request):
    """ Just a simple POST form so we can debug our code easily """
    return dict(title='Post graph')


@view_config(route_name='pushreceiver', request_method='POST', renderer='string')
def pushreceiver(request, do_apply=True):
    """ The POST receiver handler """
    global logger
    global config

    if 'content' in request.params:
        # NTriples from a form post
        ntriples = request.params['content']
    else:
        # NTriples from a SDShare push POST, it can be empty
        ntriples = request.body

        if isinstance(ntriples, bytes):
            ntriples = ntriples.decode("utf-8")

    resource_uri = request.params.get('resource')
    graph_uri = config and config.get('graph') or None

    if not graph_uri:
        graph_uri = request.params.get('graph')

    # Default response code is 200
    response = Response('OK')

    # Both parameters must be present according to the spec..
    if resource_uri is None or graph_uri is None:
        msg = 'Missing subject or graph parameters in request!'

        if logger:
            logger.error(msg)

        response =  Response(msg)
        response.status_int = 500
    else:
        # All is well, apply the data
        if logger:
            logger.info("Called with resource='%s', graph='%s'" % (resource_uri, graph_uri))
            logger.debug("NTriples: \n%s" % ntriples)
    
        if do_apply:
            try:
                if logger:
                    logger.info("Applying fragment...")

                # Try to apply fragment
                result = project_wkt(resource_uri, graph_uri, ntriples, config, logger=logger)
            except:
                # Something went wrong, log it and return non-ok error code
                result = None
                exc_type, exc_value, exc_traceback = sys.exc_info()

                if logger:
                    logger.error("Failed to apply fragment!", exc_info=(exc_type, exc_value, exc_traceback))

                response = Response('Failed to apply fragment! Traceback: %s' % ''.join(traceback.format_stack()))
                response.status_int = 500
 
            if logger:
                if not result:
                    logger.warning("The fragment did not result in any action")
                else:
                    logger.info("Fragment applied")
       
    return response


def main():
    """ Create a SDShare Push Receiver server and run it forever until stopped """
    
    global config
    global logger
    
    # Parse arguments
    parser = argparse.ArgumentParser(description="UTM to LatLong service")
    parser.add_argument("-i", "--interface", dest="interface",
                        help="Interface bind to")    
    parser.add_argument("-c", "--config", dest='configfile',
                        help='Path to config yaml file', default="config/config.yaml")
    parser.add_argument("-p", "--port", dest="port",
                        help="IP port to bind to", metavar="PORT")
    parser.add_argument("-l", "--loglevel", dest="loglevel",
                        help="Loglevel (INFO, DEBUG, WARN..), default is INFO", metavar="LOGLEVEL", default="INFO")
    parser.add_argument("-f", "--logfile", dest="logfile", default="utmtolatlongservice.log",
                        help="Filename to log to if logging to file, the default is 'utmtolatlongservice.log' in the current directory")

    options = parser.parse_args()

    # Set up logging
    format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logger = logging.getLogger('utmtolatlongservice')

    # Log to stdout
    stdout_handler = logging.StreamHandler()
    stdout_handler.setFormatter(logging.Formatter(format_string))
    logger.addHandler(stdout_handler)

    config = read_config(options.configfile, port=options.port, interface=options.interface,
                         logfile=options.logfile, loglevel=options.loglevel, logger=logger)

    logger.setLevel({"INFO": logging.INFO, "DEBUG": logging.DEBUG, "WARN": logging.WARNING,
                     "ERROR": logging.ERROR}.get(config["loglevel"], logging.INFO))

    logger.debug("Config: \n%s" % str(config))

    file_handler = logging.FileHandler(options.logfile)
    file_handler.setFormatter(logging.Formatter(format_string))
    logger.addHandler(file_handler)
    
    # Create a WSGI HTTP server and run it forever
    from pyramid.config import Configurator
    pyramid_config = Configurator()
    pyramid_config.include('pyramid_chameleon')
    pyramid_config.add_route('pushreceiver', '/')
    pyramid_config.add_route('form', '/form')
    pyramid_config.scan()

    server = make_server(config["interface"], int(config["port"]), pyramid_config.make_wsgi_app() )
    logger.info('Starting up server on http://%s:%s' % (config["interface"], config["port"]))
    server.serve_forever()


# Check if program called from the command line
if __name__ == '__main__':
    main()
