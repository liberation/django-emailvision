# -*- coding: utf-8 -*-
import codecs
import requests
import base64

from lxml import etree

from utils import Client, NotConnected, FailedApiCall, Error


class MemberAPI (object):

    response_debug = None

    def __init__(self, login, password, key, server_name):
        self.login = login
        self.password = password
        self.key = key
        self.client = Client(server_name)
        self.token = None

    def get(self, action, *values):
        if self.token is None:
            raise NotConnected()
        return self.client.get(action, *values)

    def post(self, data):
        path = '/apimember/services/MemberService?wsdl'
        return self.client.post(path, data)

    def put(self, url, xml_data=None, csv_data=None):
        if self.token is None:
            raise NotConnected()
        return self.client.put(url, xml_data, csv_data)

    def __enter__(self):
        self.__connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # FIXME: manage exceptions
        if self.token:
            self.__disconnect()

    def __connect(self):
        url = self.get_member_url(
            'connect/open/{0}/{1}/{2}'.format(
                self.login,
                self.password,
                self.key
            )
        )
        response = self.client.get(url)
        self.token = response.find('result').text

    def __disconnect(self):
        if self.token is None:
            raise NotConnected()
        url = self.get_member_url(
            'connect/close/{0}'.format(self.token)
        )
        response = self.get(url)
        return response
        self.token = None

    def get_batch_url(self, remote_method):
        output = "/apibatchmember/services/rest/{0}".format(
            remote_method
        )
        return output

    def get_member_url(self, remote_method):
        output = "/apimember/services/rest/{0}".format(
            remote_method
        )
        return output

    def insert_member_by_email(self, email):
        """returns a job id"""
        response = self.get('/apimember/services/rest/member/insert/', email)
        return response.result

    def insert_or_update_member_by_object(self, email, values):
        """returns a job id"""
        # email is the object key, so it cannot be empty
        if not email:
            raise ValueError("insert_or_update_member_by_object: email cannot be empty")
        data = u"""<?xml version="1.0" encoding="latin1" standalone="yes"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
xmlns:api="http://api.service.apimember.emailvision.com/">
<soapenv:Header/>
<soapenv:Body>
<api:insertOrUpdateMemberByObj>
<token>%s</token>
<member>
<dynContent>
""" % self.token
        for key in values:
            data += u"""<entry><key>%s</key><value>%s</value></entry>""" % (key, values[key])
        data += u"""</dynContent>
<memberUID>email:%s</memberUID>
</member>
</api:insertOrUpdateMemberByObj>
</soapenv:Body>
</soapenv:Envelope>
""" % email
        response = self.post(data)
        r = response.soap_find('Body')
        r = r.find('{http://api.service.apimember.emailvision.com/}insertOrUpdateMemberByObjResponse')
        r = r.find('return').text
        return r

    def update_member_by_email(self, email, key, value):
        """returns a job id"""
        if not value:
            raise FailedApiCall(
                Error('NO_VALUE_SET', 'No value provided'),
                self.client.server_name + '/apimember/services/MemberService?wsdl'
            )
        data = u"""<?xml version="1.0" encoding="latin1" standalone="yes"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
xmlns:api="http://api.service.apimember.emailvision.com/">
<soapenv:Header/>
<soapenv:Body>
<api:updateMember>
<token>%s</token>
<email>%s</email>
<field>%s</field>
<value>%s</value>
</api:updateMember>
</soapenv:Body>
</soapenv:Envelope>
""" % (self.token, email, key, value)
        response = self.post(data)
        r = response.soap_find('Body')
        r = r.find('{http://api.service.apimember.emailvision.com/}updateMemberResponse')
        r = r.find('return').text
        return r

    def retrieve_insert_member_job_status(self, job_id):
        # This does not work, it is always answering a 404.
        url = self.get_member_url(
            'member/getInsertMemberStatus/{0}/{1}'.format(
                self.token,
                job_id
            )
        )
        response = self.get(url)
        return response

    def __build_member_attributes(self, attributes_node):
        attributes = dict()
        for entry in attributes_node.iterfind('entry'):
            key = entry.find('key').text
            value = None
            if entry.find('value') is not None:
                value = entry.find('value').text
            attributes[key] = value
        return attributes

    def iter_over_members_by_email(self, user_email):
        url = self.get_member_url(
            'member/getMemberByEmail/{0}/{1}'.format(
                self.token,
                user_email
            )
        )
        response = self.get(url)
        for member in response.find('members').iterfind('member'):
            yield self.__build_member_attributes(member.find('attributes'))

    def retrieve_member_by_id(self, user_id):
        url = self.get_member_url(
            'member/getMemberById/{0}/{1}'.format(
                self.token,
                user_id
            )
        )
        response = self.get(url)
        attributes_nodes = response.find('apiMember').find('attributes')
        return self.__build_member_attributes(attributes_nodes)

    def member_table_column_names(self):
        url = self.get_member_url('member/descMemberTable/')
        response = self.get(url)
        entries = response.find('memberTable').find('fields').iterfind('entry')
        columns = dict()
        for entry in entries:
            key = entry.find('key').text
            value = entry.find('value').text
            columns[key] = value
        return columns

    def unsubscribe_members_by_email(self, user_email):
        """returns a job id"""
        url = self.get_member_url(
            'member/unjoinByEmail/{0}/{1}'.format(
                self.token,
                user_email
            )
        )
        response = self.get(url)
        return response.result

    def unsubscribe_members_by_id(self, user_id):
        """returns a job id"""
        url = self.get_member_url(
            'member/unjoinByMemberId/{0}/{1}'.format(
                self.token,
                user_id
            )
        )
        response = self.get(url)
        return response.result

    def resubscribe_members_by_email(self, user_email):
        """returns a job id"""
        url = self.get_member_url(
            'member/rejoinByEmail/{0}/{1}'.format(
                self.token,
                user_email
            )
        )
        response = self.get(url)
        return response.result

    def resubscribe_members_by_id(self, user_id):
        """returns a job id"""
        url = self.get_member_url(
            'member/rejoinByMemberId/{0}/{1}'.format(
                self.token,
                user_id
            )
        )
        response = self.client.get(url)
        return response.result

    def assemble_upstream_body(self, parameters):
        if not isinstance(parameters, EMVAPIMergeUploadParams):
            return "something went wrong check your parameters"
        mergeUpload = etree.Element('mergeUpload')
        criteria = etree.SubElement(mergeUpload, 'criteria')
        criteria.text = parameters.criteria
        file_name = etree.SubElement(mergeUpload, 'fileName')
        file_name.text = parameters.path.split('/')[-1]
        separator = etree.SubElement(mergeUpload, 'separator')
        separator.text = parameters.separator
        file_encoding = etree.SubElement(mergeUpload, 'fileEncoding')
        file_encoding.text = parameters.file_encoding
        skip_first_line = etree.SubElement(mergeUpload, 'skipFirstLine')
        skip_first_line.text = parameters.skip_first_line
        mapping = etree.SubElement(mergeUpload, 'mapping')
        for param in parameters.mapping:
            column = etree.SubElement(mapping, 'column')
            for key, value in param.iteritems():
                node = etree.SubElement(column, key)
                node.text = str(value)

        data = etree.tostring(
            mergeUpload,
            xml_declaration=True,
            encoding="UTF-8",
            pretty_print=True
        )

        return data

    def upload_file_merge(self, parameters):
        if not self.token:
            return "You should try to connect first!"
        url = self.get_batch_url(
            'batchmemberservice/{0}/batchmember/mergeUpload'.format(self.token)
            )

        data = self.assemble_upstream_body(parameters)
        response = self.put(url, data, parameters.file_content)
        return u"Upload status : {0}".format(
            self.get_last_upload_status()
        )

    def get_log_file(self, upload_id=None):
        if not upload_id:
            upload_id = self.get_last_upload_id()

        url = self.get_batch_url(
            'batchmemberservice/{0}/batchmember/{1}/getLogFile'.format(
                self.token,
                upload_id
            )
        )
        response = self.get(url)
        return response.result

    def get_bad_file(self, upload_id=None):
        if not upload_id:
            upload_id = self.get_last_upload_id()

        url = self.get_batch_url(
            'batchmemberservice/{0}/batchmember/{1}/getBadFile'.format(
                self.token,
                upload_id
            )
        )
        response = self.get(url)
        return response.result

    def get_last_upload_status(self):
        url = self.get_batch_url(
            'batchmemberservice/{0}/batchmember/getLastUpload'.format(self.token)
        )
        response = self.client.get(url)
        return response.find('lastUploads[1]/status').text

    def get_last_upload_id(self):
        url = self.get_batch_url(
            'batchmemberservice/{0}/batchmember/getLastUpload'.format(self.token)
        )
        response = self.client.get(url)
        return response.find('lastUploads[1]/id').text


class EMVAPIMergeUploadParams(object):

    def __init__(
        self,
        path,
        file_encoding,
        separator,
        criteria,
        skip_first_line,
        mapping
    ):
        self.path = path
        self.file_encoding = file_encoding
        self.separator = separator
        self.criteria = criteria
        self.skip_first_line = skip_first_line
        self.mapping = mapping
        self.file_content = base64.b64encode(
            codecs.open(self.path, 'r', 'utf-8').read()
        )
