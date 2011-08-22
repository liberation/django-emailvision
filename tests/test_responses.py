from unittest import TestCase
from types import GeneratorType

from emailvision.utils import BaseResponse, GetResponse, PostResponse


class BaseResponseTest(TestCase):
    klass = BaseResponse

    def test_find(self):
        base_response = klass(u'<xml><a><b></b></a></xml>')
        a_element = base_response.find('a')
        self.assertIsNotNone(a_element)
        self.assertEquals(len(a_element.getchildren()), 1)

    def test_findall(self):
        base_response = klass(u'<xml><a><b></b></a><a></a></xml>')
        a_elements = base_response.findall('a')
        self.assertEquals(len(a_elements), 2)
        self.assertEquals(len(a_elements[0].getchildren()), 1)
        self.assertEquals(len(a_elements[1].getchildren()), 0)

    def test_iterfind(self):
        base_response = klass(u'<xml><a><b></b></a><a></a></xml>')
        a_elements = base_response.iterfind('a')
        self.assertEquals(type(a_elements), GeneratorType)
        nb_childs_of_a_elements = [1, 0]
        for index, a_element in enumerate(a_elements):
            self.assertEquals(len(a_element.getchildren()), nb_childs_of_a_elements[index])
        self.assertEquals(index, 1)


class PostResponseTest(BaseResponseTest):
    klass = PostResponse
