from unittest import TestCase
from types import GeneratorType

from emailvision.utils import BaseResponse, GetResponse, PostResponse


class BaseResponseTest(TestCase):
    klass = BaseResponse

    def test_find(self):
        base_response = self.klass('<?xml version="1.0" encoding="utf-8" standalone="yes"?><root><a><b></b></a></root>')
        a_element = base_response.find('a')
        self.assertIsNotNone(a_element)
        self.assertEquals(len(a_element.getchildren()), 1)

    def test_findall(self):
        base_response = self.klass('<?xml version="1.0" encoding="utf-8" standalone="yes"?><root><a><b></b></a><a></a></root>')
        a_elements = base_response.findall('a')
        self.assertEquals(len(a_elements), 2)
        self.assertEquals(len(a_elements[0].getchildren()), 1)
        self.assertEquals(len(a_elements[1].getchildren()), 0)

    def test_iterfind(self):
        base_response = self.klass('<?xml version="1.0" encoding="utf-8" standalone="yes"?><root><a><b></b></a><a></a></root>')
        a_elements = base_response.iterfind('a')
        self.assertEquals(type(a_elements), GeneratorType)
        nb_childs_of_a_elements = [1, 0]
        for index, a_element in enumerate(a_elements):
            self.assertEquals(len(a_element.getchildren()), nb_childs_of_a_elements[index])
        self.assertEquals(index, 1)


class GetResponseTest(BaseResponseTest):
    klass = GetResponse

    def test_success_true(self):
        response = GetResponse("""<?xml version="1.0" encoding="utf-8" standalone="yes"?>
<response responseStatus="success"></response>""")
        self.assertTrue(response.success)

    def test_success_false(self):
        response = GetResponse("""<?xml version="1.0" encoding="utf-8" standalone="yes"?>
<response responseStatus="failed"></response>""")
        self.assertFalse(response.success)

    def test_result(self):
        response = GetResponse("""<?xml version="1.0" encoding="utf-8" standalone="yes"?><response responseStatus="success"><result xsi:type="xs:string" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xs="http://www.w3.org/2001/XMLSchema">OK</result></response>""")
        self.assertEquals(response.result, 'OK')

    def test_error(self):
        response = GetResponse("""<?xml version="1.0" encoding="utf-8" standalone="yes"?><response responseStatus="failed"><description>{{ description }}</description><fields>azeaze</fields><status>{{ status }}</status></response>""")
        self.assertEquals(response.error.status, '{{ status }}')
        self.assertEquals(response.error.description, '{{ description }}')


class PostResponseTest(BaseResponseTest):
    klass = PostResponse
