# -*- coding: utf-8 -*-

from wktprojectionservice.config import default_config
from wktprojectionservice import receiver
from wktprojectionservice.convert import project_wkt

import logging

class FakeResponse:
    def __init__(self):
        self.content_type = ""


class FakeRequest:
    def __init__(self, resource, graph, body):
        self.params = {"content": body, "resource": resource, "graph": graph}
        self.response = FakeResponse()


class FakePostHandler:    
    def __init__(self):
        self.posts = []

    def post_handler(self, endpoint, resource_uri, graph, ntriples, logger=None):
        self.posts.append((endpoint, resource_uri, graph, ntriples))

        return "OK"
    
    def clear(self):
        self.posts = []


def test_request():
    with open("wktprojectionservice/testdata/test.nt","r") as inputfile:
        req = FakeRequest("https://example.com/1", "http://psi.test.no/graph",  inputfile.read())
        result = receiver.pushreceiver(req, do_apply=False)

        assert result.status_int == 200


def test_point ():
    fake = FakePostHandler()

    # Source coordinate system here is EPSG:25833, and not EPSG:32632 as in def conf
    fake_config = dict(port="6543"
                       , interface="0.0.0.0"
                       , endpoint="http://localhost:9001/api/sinks/test-sink/entities"
                       , graph=""
                       , sourceCoordinateSystem="EPSG:25833"
                       , targetCoordinateSystem="EPSG:4326"
                       , switch_x_y=False
                       , switch_x_y_out=False
                       , sourceGeometry="https://example.com/etrs89"
                       , targetGeometry="http://example.com/wgs84_pos#lat_long"
                       , targetDatatype="http://www.openlinksw.com/schemas/virtrdf#Geometry"
                       , logfile="wktprojectionservice.log"
                       , loglevel=logging.INFO
                   )

    with open("wktprojectionservice/testdata/point.nt","r") as inputfile:
        data = inputfile.read()

        assert project_wkt("https://example.com/1", "http://data.sesam.io/1", data, fake_config,
                           post_handler=fake.post_handler, logger=None)

        assert len(fake.posts) == 1

        assert fake.posts[0][0] == 'http://localhost:9001/api/sinks/test-sink/entities'
        assert fake.posts[0][1] == 'https://example.com/1'
        assert fake.posts[0][2] == 'http://data.sesam.io/1'

        assert fake.posts[0][3].find('<https://example.com/1> <http://example.com/wgs84_pos#lat_long> "POINT (59.9395763471 10.7225526358)"^^<http://www.openlinksw.com/schemas/virtrdf#Geometry> .') > -1


    fake.clear()

def test_multipolygon():
    fake = FakePostHandler()

    fake_config = default_config

    with open("wktprojectionservice/testdata/multipolygon.nt","r") as inputfile:
        data = inputfile.read()

        assert project_wkt("https://example.com/1", "http://data.sesam.io/1", data, fake_config,
                           post_handler=fake.post_handler, logger=None)

        assert len(fake.posts) == 1

        assert fake.posts[0][0] == 'http://localhost:9001/api/sinks/test-sink/entities'
        assert fake.posts[0][1] == 'https://example.com/1'
        assert fake.posts[0][2] == 'http://data.sesam.io/1'

        assert fake.posts[0][3].find('<https://example.com/1> <http://example.com/wgs84_pos#lat_long> "MULTIPOLYGON (((60.3419563363 2.8836725689, 60.3419852976 2.8836769606, 60.3420131197 2.8836521422, 60.3420286560 2.8835880457, 60.3420235934 2.8835307627, 60.3419985229 2.8835173697, 60.3419762553 2.8835253143, 60.3419601456 2.8835703142, 60.3419518149 2.8835961836, 60.3419429421 2.8836389099, 60.3419563363 2.8836725689)), ((60.3408869409 2.8832765536, 60.3408867030 2.8832449060, 60.3408669539 2.8832472848, 60.3408657642 2.8832760776, 60.3408869409 2.8832765536)), ((60.3421879065 2.8831297151, 60.3421879065 2.8831137775, 60.3421763653 2.8831150594, 60.3421763653 2.8831300813, 60.3421879065 2.8831297151)))"^^<http://www.openlinksw.com/schemas/virtrdf#Geometry> .') > -1

    fake.clear()


def test_conversion():
    fake = FakePostHandler()
    
    fake_config = default_config
    
    with open("wktprojectionservice/testdata/test.nt","r") as inputfile:
        data = inputfile.read()
   
        assert project_wkt("https://example.com/1", "http://data.sesam.io/1", data, fake_config,
                           post_handler=fake.post_handler, logger=None)

        assert len(fake.posts) == 1

        assert fake.posts[0][0] == 'http://localhost:9001/api/sinks/test-sink/entities'
        assert fake.posts[0][1] == 'https://example.com/1'
        assert fake.posts[0][2] == 'http://data.sesam.io/1'
        assert fake.posts[0][3].find('<https://example.com/1> <http://example.com/wgs84_pos#lat_long> "MULTIPOLYGON (((0.0003607752 4.5116144752, 0.0004058720 4.5114352951, 0.0002705814 4.5116592702, 0.0003607752 4.5116144752)), ((0.0003156782 4.5114352952, 0.0002705813 4.5113457052, 0.0000901938 4.5113457053, 0.0000450969 4.5115248852, 0.0001803876 4.5116592702, 0.0003156782 4.5114352952),(0.0001803876 4.5115248852, 0.0001352907 4.5114352952, 0.0002254845 4.5114352952, 0.0001803876 4.5115248852)))"^^<http://www.openlinksw.com/schemas/virtrdf#Geometry> .\n') > -1
        assert fake.posts[0][3].find('<https://example.com/1> <http://example.com/wgs84_pos#lat_long> "POLYGON ((59.0534600463 2.4626771965, 59.0534653609 2.4627288402, 59.0534708750 2.4627488754, 59.0534766682 2.4627617035, 59.0534938483 2.4627858887, 59.0535017289 2.4627934363, 59.0535102159 2.4627978536, 59.0535304157 2.4628012586, 59.0535391277 2.4627990352, 59.0535500805 2.4627910386, 59.0535685282 2.4627683974, 59.0535751359 2.4627571536, 59.0535843755 2.4627283249, 59.0535898200 2.4626919560, 59.0535909690 2.4626693502, 59.0535890649 2.4626469371, 59.0535834919 2.4626172167, 59.0535786118 2.4626030304, 59.0535644826 2.4625745175, 59.0535496314 2.4625565820, 59.0535339783 2.4625489977, 59.0535252096 2.4625478781, 59.0535164976 2.4625501015, 59.0534983862 2.4625607370, 59.0534905046 2.4625682771, 59.0534814573 2.4625826846, 59.0534638310 2.4626327578, 59.0534604319 2.4626544935, 59.0534600463 2.4626771965))"^^<http://www.openlinksw.com/schemas/virtrdf#Geometry> .\n') > -1

    fake.clear()
    
    with open("wktprojectionservice/testdata/test_error.nt","r") as inputfile:
        data = inputfile.read()
   
        assert project_wkt("https://example.com/1", "http://data.sesam.io/1", data, fake_config,
                           post_handler=fake.post_handler, logger=None)
        
        assert len(fake.posts) == 0

    fake.clear()

    with open("wktprojectionservice/testdata/test_error_empty.nt","r") as inputfile:
        data = inputfile.read()

    assert project_wkt("https://example.com/1", "http://data.sesam.io/1", data, fake_config,
                       post_handler=fake.post_handler, logger=None)

    assert fake.posts[0][0] == 'http://localhost:9001/api/sinks/test-sink/entities'
    assert fake.posts[0][1] == 'https://example.com/1'
    assert fake.posts[0][2] == 'http://data.sesam.io/1'
    assert fake.posts[0][3] == ''

if __name__ == '__main__':
    test_request()
    test_conversion()
