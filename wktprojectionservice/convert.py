# -*- coding: utf-8 -*-

import rdflib
from pyproj import Proj, transform
from pygeoif import geometry
import requests

def postfragment(endpoint, resource_uri, graph, ntriples, logger=None):
    if logger:
        logger.debug("Posting fragment to endpoint '%s': %s" % (endpoint, ntriples))

    body = ntriples.encode('utf-8')
    params = {"resource": resource_uri, "graph": graph}

    r = requests.post(endpoint, params=params, data=body)

    logger.debug("Response: " + str(r.text))

    if logger:
        logger.debug("Request status: %s, %s" % (r.status_code, r.reason))

    if r.status_code != 200:
        if logger:
            logger.error("Failed to do HTTP post, response was: %s " % r.text)

        raise Exception("PostError")

    return r.text

def project_coord(config, coord, source_projection, target_projection, logger=None):
    if len(coord) != 2:
        if logger is not None:
            logger.error("Found coordinates with more than two components in: '%s'" % p.to_wkt())
        raise Exception("Only 2D coordinates are supported")

    if config.get("switch_x_y", False):
        y, x = coord
    else:
        x, y = coord

    if config.get("switch_x_y_out", False):
        lat, long = transform(source_projection, target_projection, x, y)
    else:
        long, lat = transform(source_projection, target_projection, x, y)
    return format (lat, '.10f'), format (long, '.10f')

def project_wkt_point (config, p, source_projection, target_projection, logger=None):
    geo = p.__geo_interface__
    return ("%s %s" % project_coord (config, geo["coordinates"], source_projection, target_projection, logger))



def project_wkt_polygon(config, p, source_projection, target_projection, logger=None):
    polygons = []
    geo = p.__geo_interface__

    for poly in geo["coordinates"]:
        polygon = []
        for coord in poly:
            polygon.append("%s %s" % (project_coord (config, coord, source_projection, target_projection, logger)))
        polygons.append("(%s)" % ", ".join(polygon))

    return "(%s)" % (",".join(polygons))


def project_wkt(resource_uri, graph_uri, ntriples, config, post_handler=postfragment, logger=None):
    graph = rdflib.Graph()

    try:
        graph.parse(data=ntriples, format="nt")
    except Exception as e:
        s = "Failed to parse input fragment '%s'... RDFLib says the reason is '%s'" % (ntriples, e.message)
        if logger:
            logger.exception(s)
        raise e

    subject_filter = rdflib.term.URIRef(resource_uri)
    wkt_uri = rdflib.term.URIRef(config['sourceGeometry'])
    wkt_res = [t for t in graph.triples((subject_filter, wkt_uri, None))]

    if graph.__len__() == 0:
        if logger:
            s = "Received empty fragment. Deleting'%s'" % config['sourceGeometry']
            logger.info(s)
        post_handler(config["endpoint"], resource_uri, graph_uri, ntriples, logger=logger)
        return True

    if len(wkt_res) == 0:
        if logger:
            s = "No geometry matching predicate '%s' found in fragment, skipping..." % config['sourceGeometry']
            logger.warning(s)
        return True

    triples = ""
    source_projection = Proj(init=config['sourceCoordinateSystem'])
    target_projection = Proj(init=config['targetCoordinateSystem'])

    for s, p, value in wkt_res:
        p = geometry.from_wkt(value.strip())

        if isinstance(p, geometry.Polygon):
            projected_s = "POLYGON " + project_wkt_polygon(config, p,
                                                            source_projection,
                                                            target_projection, logger=logger) + ""

            triples += '<%s> <%s> "%s"^^<%s> .\n' % (resource_uri, config['targetGeometry'], projected_s,
                                                     config.get("targetDatatype",
                                                                "http://www.w3.org/2001/XMLSchema#string"))

        elif isinstance(p, geometry.MultiPolygon):
            polygons = []

            for polygon in p.geoms:
                polygons.append(project_wkt_polygon(config, polygon, source_projection,
                                                    target_projection, logger=logger))

            projected_s = "MULTIPOLYGON (" + ", ".join(polygons) + ")"

            triples += '<%s> <%s> "%s"^^<%s> .\n' % (resource_uri, config['targetGeometry'], projected_s,
                                                     config.get("targetDatatype",
                                                                "http://www.w3.org/2001/XMLSchema#string"))
        elif isinstance(p, geometry.Point):
            projected_s = "POINT (" + project_wkt_point(config, p, source_projection, target_projection,
                                                         logger=logger) + ")"

            triples += '<%s> <%s> "%s"^^<%s> .\n' % (resource_uri, config['targetGeometry'], projected_s,
                                                     config.get("targetDatatype",
                                                                "http://www.w3.org/2001/XMLSchema#string"))

    post_handler(config["endpoint"], resource_uri, graph_uri, triples, logger=logger)

    return True
