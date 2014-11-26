# -*- coding: utf-8 -*-
import requests

from collections import namedtuple

try:
    from lxml import etree
except ImportError:
    try:
        # Python 2.5
        import xml.etree.cElementTree as etree
    except ImportError:
        try:
            # Python 2.5
            import xml.etree.ElementTree as etree
        except ImportError:
            try:
                # normal cElementTree install
                import cElementTree as etree
            except ImportError:
                # normal ElementTree install
                import elementtree.ElementTree as etree


Error = namedtuple('Error', ['status', 'description'])


class BadResponse(Exception):
    """This means that emailvision fails to answer the request"""
    def __init__(self, message):
        super(Exception, self).__init__(message)


class FailedApiCall(Exception):
    """The API call is not legit"""
    def __init__(self, error, url):
        super(Exception, self).__init__('%s: %s. url is %s ' % (error.status, error.description, url))


class NotConnected(Exception):
    pass


class Client(object):

    def __init__(self, server_name):
        self.server_name = 'https://' + server_name

    def get(self, action_path, *values):
        url = ''.join((self.server_name, action_path))
        response = requests.get(url)
        if response.status_code == 500:
            raise FailedApiCall(GetResponse(response.content).error, url)
        if response.status_code != 200:
            msg = 'Server `%s` answered %s status for `%s`.\n%s'
            raise BadResponse(msg % (self.server_name,
                                     response.status_code,
                                     url,
                                     response.content))
        if response.headers['content-type'] == 'text/xml':
            msg = 'Server `%s` answered %s content-type for `%s`.\n%s'
            raise BaseResponse(msg % (self.server_name,
                                      response.headers['content-type'],
                                      url,
                                      response.content))
        response = GetResponse(response.content)
        return response

    def post(self, path, data):
        url = self.server_name + path
        response = requests.post(url, data.encode('latin1', 'ignore'))
        return PostResponse(response.content)

    def put(self, url, xml_data=None, csv_data=None):
        url = self.server_name + url
        files = {
            'mergeUpload': ('export_user.xml', xml_data, 'text/xml'),
            'inputStream': (
                'dump.csv',
                csv_data,
                'application/octet-stream\r\nContent-Transfer-Encoding: base64'
                )
            }
        response = requests.put(url, files=files)
        if response.status_code == 500:
            raise FailedApiCall(GetResponse(response.content).error, url)

        if response.status_code != 200:
            msg = 'Server `%s` answered %s status for `%s`.\n%s'
            raise BadResponse(msg % (self.server_name,
                                     response.status_code,
                                     url,
                                     response.content))

        response = GetResponse(response.content)
        return response


class BaseResponse (object):

    def __init__(self, f):
        parser = etree.XMLParser()
        self.f = f  # FIXME: debug purpose
        self.root = etree.fromstring(f, parser)

    def find(self, xpath_query):
        """Finds the first element using XPath."""
        return self.root.find(xpath_query)

    def findall(self, xpath_query):
        """Finds all elements using XPath."""
        return self.root.find(xpath_query)

    def iterfind(self, xpath_query):
        """Returns an iterator over the elements found using the XPath"""
        return self.root.iterfind(xpath_query)


class GetResponse (BaseResponse):

    def __init__(self, f):
        super(GetResponse, self).__init__(f)

    @property
    def result(self):
        return self.find('result').text

    @property
    def success(self):
        return self.root.attrib['responseStatus'] == 'success'

    @property
    def error(self):
        description = self.find('description').text
        status = self.find('status').text
        return Error(status, description)


class PostResponse (BaseResponse):

    def __init__(self, f):
        super(PostResponse, self).__init__(f)

    @property
    def result(self):
        return None  # FIXME: to implement

    @property
    def success(self):
        return None  # FIXME: to implement

    @property
    def error(self):
        return None  # FIXME: to implement

    def soap_find(self, xpath):
        return self.find('{%s}%s' % ('http://schemas.xmlsoap.org/soap/envelope/',
                                     xpath))
