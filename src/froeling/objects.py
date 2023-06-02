import datetime

from . import endpoints


class Datapoint:
    """Stores data like the value, unit and name of a datapoint."""
    string_list = {}

    def __init__(self, data):
        self.id = data['id']
        self.display_name = data['displayName']
        self.name = data['name']
        self.type = data['parameterType']
        self.unit = data['unit']
        self.value = data['value']

        if self.type == "StringValueObject":
            self.string_list = data['stringListKeyValues']

    def get(self):
        if self.string_list:
            return self.string_list[self.value]
        else:
            return self.value + self.unit


class Component:
    """Stores general information and a list of all Datapoints of this component."""
    data: dict = []
    datapoints: list[Datapoint] = []

    display_category: str
    standard_name: str
    component_number: int
    type: str
    sub_type: str
    picture: str

    def __init__(self, facility_id, component_id, session, display_name=None, _type=None):
        self.session = session
        self.facility_id = facility_id
        self.component_id = component_id
        self.display_name = display_name
        self.type = _type

    async def get_data(self):
        """Gets all data of this component"""
        res: dict = await self.session.request('get', endpoints.COMPONENT.format(self.session.user_id, self.facility_id, self.component_id))
        self.data = res
        self.display_name = res['displayName']
        self.display_category = res['displayCategory']
        self.standard_name = res['standardName']
        self.component_number = res['componentNumber']
        self.type = res['type']
        self.sub_type = res['subType'] if 'subType' in res else None
        self.picture = res['topView']['pictureUrl']

        datapoint_data = res['stateView']+res['setupView']+list(res['topView']['configParams'].values())+list(res['topView']['infoParams'].values())
        self.datapoints = [Datapoint(i) for i in datapoint_data]


class Facility:
    """Stores the data of a facility."""

    components: dict[str, Component] = {}
    """Stores all components of this facility (Initiated/Updated with get_components())."""

    def __init__(self, facility_id, session):
        self.id = facility_id
        self.session = session

    async def get_components(self):
        """Gets all components of this Facility and stores them in self.components"""
        res = await self.session.request("get", endpoints.COMPONENT_LIST.format(self.session.user_id, self.id))
        self.components = {c['componentId']: Component(self.id, c['componentId'], self.session, display_name=c['displayName'], _type=c['type']) for c in res}


class Notification:
    """Stores the data of a notification."""

    body = None
    sms = None
    mail = None
    push = None
    submitted_to = None
    errorSolutions = None

    def __init__(self, data, session):
        self.session = session
        self.data = data

        self.notification_id = data['id']
        self.subject = data['subject']
        self.unread = data['unread']
        self.date = datetime.datetime.fromisoformat(data['notificationDate'])
        self.error_id = data['errorId']
        self.notification_type = data['notificationType']
        self.facility_id = data['facilityId']
        self.facility_name = data['facilityName']

    """Gets additional information about this notification."""
    async def info(self):
        res = await self.session.request("get", endpoints.NOTIFICATION.format(self.session.user_id, self.notification_id))
        self.body = res['body']
        self.sms = res['sms']
        self.mail = res['mail']
        self.push = res['push']
        self.submitted_to = res['notificationSubmissionStateDto']
        self.errorSolutions = res['errorSolutions']

        return res
