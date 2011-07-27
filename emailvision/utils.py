from collections import namedtuple
from urllib import quote

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

from httplib2 import Http


Error = namedtuple('Error', ['status', 'description'])


class BadResponse(Exception):
    def __init__(self, message):
        super(Exception, self).__init__(message)

class FailedApiCall(Exception):
    def __init__(self, error, url):
        super(Exception, self).__init__('%s: %s. url is %s ' % (error.status, error.description, url))

class NotConnected(Exception):
    pass


class Client(object):

    def __init__(self, server_name):
        self.http = Http()
        self.server_name = 'https://' + server_name

    def get(self, action_path, *values):
        path = action_path + '/'.join([quote(unicode(value)) for value in values])
        url = ''.join((self.server_name, path))
        response, content = self.http.request(url)

        if response['status'] == '500':
            raise FailedApiCall(GetResponse(content).error, url)
        if response['status'] != '200':
            msg = 'Server `%s` answered %s status for `%s`.\n%s'
            raise BadResponse(msg % (self.server_name,
                                     response['status'],
                                     url,
                                     content))
        if response['content-type'] == 'text/xml':
            msg = 'Server `%s` answered %s content-type for `%s`.\n%s'
            raise BaseResponse(msg % (self.server_name,
                                      response['content-type'],
                                      url,
                                      content))
        response = GetResponse(content)
        return response

    def post(self, path, data):
        url = self.server_name + path
        response, content = self.http.request(url, 'POST', data)
        return PostResponse(content)


class BaseResponse (object):

    def __init__(self, f):
        self.f = f
        self.root = etree.fromstring(f)

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
        self.f = f  # FIXME: remove it
        self.root = etree.fromstring(f)

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
        return None

    @property
    def success(self):
        return None

    @property
    def error(self):
        return None

    def soap_find(self, xpath):
        return self.find('{%s}%s' % ('http://schemas.xmlsoap.org/soap/envelope/',
                                     xpath))

