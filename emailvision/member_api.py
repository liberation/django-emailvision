from utils import Client, NotConnected, FailedApiCall, Error


class MemberAPI (object):

    def __init__(self, login, password, key, server_name):
        self.login = login
        self.password = password
        self.key = key
        self.client = Client(server_name)
        self.token = None

    def get(self, action, *values):
        if self.token is None:
            raise NotConnected()
        return self.client.get(action,
                               self.token,
                               *values)

    def post(self, data):
        path = '/apimember/services/MemberService?wsdl'
        return self.client.post(path, data)

    def __enter__(self):
        self.__connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # FIXME: manage exceptions
        self.__disconnect()

    def __connect(self):
        response = self.client.get('/apimember/services/rest/connect/open/',
                                   self.login,
                                   self.password,
                                   self.key)
        self.token = response.find('result').text

    def __disconnect(self):
        if self.token is None:
            raise NotConnected()
        self.client.get('/apimember/services/rest/connect/close/', self.token)
        self.token = None

    def insert_member_by_email(self, email):
        """returns a job id"""
        response = self.get('/apimember/services/rest/member/insert/', email)
        return response.result

    def insert_or_update_member_by_object(self, email, values):
        """returns a job id"""
        data = """<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
xmlns:api="http://api.service.apimember.emailvision.com/">
<soapenv:Header/>
<soapenv:Body>
<api:insertOrUpdateMemberByObj>
<token>%s</token>
<member>
<dynContent>
""" % self.token
        for key in values:
            data += """<entry><key>%s</key><value>%s</value></entry>""" % (key, values[key])
        data += """</dynContent>
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
            raise FailedApiCall(Error('NO_VALUE_SET', 'No value provided'), self.client.server_name + '/apimember/services/MemberService?wsdl')
        data = """<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
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
        response = self.get('/apimember/services/rest/member/getInsertMemberStatus/', str(job_id))
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

    def iter_over_members_by_email(self, email):
        response = self.get('/apimember/services/rest/member/getMemberByEmail/', email)
        for member in response.find('members').iterfind('member'):
            yield self.__build_member_attributes(member.find('attributes'))

    def retrieve_member_by_id(self, id):
        response = self.get('/apimember/services/rest/member/getMemberById/', str(id))
        attributes_nodes = response.find('apiMember').find('attributes')
        return self.__build_member_attributes(attributes_nodes)

    def iter_over_members_by_page(self, page):
        response = self.get('/apimember/services/rest/getListMembersByPage/', str(page))
        for member in response.find('result').iterfind('list'):
            yield self.__build_member_attributes(member.find('attributes'))

    def member_table_column_names(self):
        response = self.get('/apimember/services/rest/member/descMemberTable/')
        entries = response.find('memberTable').find('fields').iterfind('entry')
        columns = dict()
        for entry in entries:
            key = entry.find('key').text
            value = entry.find('value').text
            columns[key] = value
        return columns

    def unsubscribe_members_by_email(self, email):
        """returns a job id"""
        response = self.get('/apimember/services/rest/member/unjoinByEmail/', email)
        return response.result

    def unsubscribe_members_by_id(self, id):
        """returns a job id"""
        response = self.get('/apimember/services/rest/member/unjoinByMemberId/', str(id))
        return response.result

    def resubscribe_members_by_email(self, email):
        """returns a job id"""
        response = self.get('/apimember/services/rest/member/rejoinByEmail/', str(id))
        return response.result

    def resubscribe_members_by_id(self, id):
        """returns a job id"""
        response = self.get('/apimember/services/rest/member/rejoinByMemberId/', str(id))
        return response.result

