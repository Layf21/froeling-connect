from dataclasses import dataclass
import datetime

from .. import endpoints

class NotificationOverview:
    """Stores basic data of a notification."""
    id: int
    subject: str
    unread: bool
    date: datetime.date
    error_id: int
    type: str
    """Known Values: "ERROR", "INFO", "WARNING", "ALARM" """
    facility_id: int
    facility_name: str

    details: 'NotificationDetails'

    def __init__(self, data, session):
        self.session = session
        self.set_data(data)

    def set_data(self, data):
        self.data = data

        self.id = data.get('id')
        self.subject = data.get('subject')
        self.unread = data.get('unread')
        self.date = datetime.datetime.fromisoformat(data.get('notificationDate'))
        self.error_id = data.get('errorId')
        self.type = data.get('notificationType')
        self.facility_id = data.get('facilityId')
        self.facility_name = data.get('facilityName')

    """Gets additional information about this notification."""
    async def info(self):
        res = await self.session.request("get", endpoints.NOTIFICATION.format(self.session.user_id, self.id))
        self.details = NotificationDetails.from_dict(res)
        return self.details


@dataclass
class NotificationDetails(NotificationOverview):
    """Stores all data of a notification"""
    body: str
    sms: bool
    mail: bool
    push: bool
    notification_submission_state_dto: list['NotificationSubmissionState']
    errorSolutions: list['NotificationErrorSolutions']

    @classmethod
    def from_dict(cls, obj):
        body = obj.get("body")
        sms = obj.get("sms")
        mail = obj.get("mail")
        push = obj.get("push")
        submission_state = None
        if "notificationSubmissionStateDto" in obj:
            submission_state = NotificationSubmissionState.from_list(obj["notificationSubmissionStateDto"])
        error_solutions = None
        if "errorSolutions" in obj:
            error_solutions = NotificationErrorSolutions.from_list(obj["errorSolutions"])
        notificationDetailsObject = cls(body, sms, mail, push, submission_state, error_solutions)
        notificationDetailsObject.set_data(obj)
        return notificationDetailsObject

@dataclass
class NotificationSubmissionState:
    id: int
    recipient: str
    type: str
    submitted_to: str
    submission_result: str


    @classmethod
    def from_dict(cls, obj: dict) -> 'NotificationSubmissionState':
        _id = obj.get('id')
        recipient = obj.get('recipient')
        type = obj.get('type')
        """Known values: "EMAIL", "TOKEN" """
        submitted_to = obj.get('submittedTo')
        submission_result = obj.get('submissionResult')

        return NotificationSubmissionState(_id, recipient, type, submitted_to, submission_result)

    @classmethod
    def from_list(cls, obj: list[dict]):
        return [cls.from_dict(i) for i in obj]


@dataclass
class NotificationErrorSolutions:
    error_reason: str
    error_solution: str

    @classmethod
    def from_list(cls, obj: list[dict]) -> list['NotificationErrorSolutions']:
        return [cls(i['errorReason'], i['errorSolution']) for i in obj]