"""Datamodels to represent Notifications and related objects."""

import datetime
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from froeling.session import Session

from froeling import endpoints


class NotificationOverview:
    """Stores basic data of a notification."""

    id: int | None
    subject: str | None
    unread: bool | None
    date: datetime.date | None
    error_id: int | None
    type: str | None
    """Known Values: "ERROR", "INFO", "WARNING", "ALARM" """
    facility_id: int | None
    facility_name: str | None

    details: 'NotificationDetails'

    def __init__(self, data: dict, session: 'Session') -> None:
        """Create a new NotificationOverview."""
        self.session = session
        self._set_data(data)

    def _set_data(self, data: dict) -> None:
        self.data = data

        self.id = data.get('id')
        self.subject = data.get('subject')
        self.unread = data.get('unread')
        date_str = data.get('notificationDate')
        if isinstance(date_str, str):
            self.date = datetime.datetime.fromisoformat(date_str)
        else:
            self.date = None
        self.error_id = data.get('errorId')
        self.type = data.get('notificationType')
        self.facility_id = data.get('facilityId')
        self.facility_name = data.get('facilityName')

    async def info(self) -> 'NotificationDetails':
        """Get additional information about this notification."""
        res = await self.session.request('get', endpoints.NOTIFICATION.format(self.session.user_id, self.id))
        self.details = NotificationDetails._from_dict(res)  # noqa: SLF001
        return self.details


@dataclass
class NotificationDetails(NotificationOverview):
    """Stores all data related to a notification."""

    body: str | None
    sms: bool | None
    mail: bool | None
    push: bool | None
    notification_submission_state_dto: list['NotificationSubmissionState'] | None
    error_solutions: list['NotificationErrorSolution'] | None

    @classmethod
    def _from_dict(cls, obj: dict) -> 'NotificationDetails':
        body = obj.get('body')
        sms = obj.get('sms')
        mail = obj.get('mail')
        push = obj.get('push')
        submission_state = None
        if 'notificationSubmissionStateDto' in obj:
            submission_state = NotificationSubmissionState._from_list(obj['notificationSubmissionStateDto'])  # noqa: SLF001
        error_solutions = None
        if 'errorSolutions' in obj:
            error_solutions = NotificationErrorSolution._from_list(obj['errorSolutions'])  # noqa: SLF001
        notification_details_object = cls(body, sms, mail, push, submission_state, error_solutions)
        notification_details_object._set_data(obj)  # noqa: SLF001
        return notification_details_object


@dataclass
class NotificationSubmissionState:
    """Submission state of a notification."""

    id: int | None
    recipient: str | None
    type: str | None
    submitted_to: str | None
    submission_result: str | None

    @classmethod
    def _from_dict(cls, obj: dict) -> 'NotificationSubmissionState':
        notification_id = obj.get('id')
        recipient = obj.get('recipient')
        notification_type = obj.get('type')
        """Known values: "EMAIL", "TOKEN" """
        submitted_to = obj.get('submittedTo')
        submission_result = obj.get('submissionResult')

        return NotificationSubmissionState(
            notification_id,
            recipient,
            notification_type,
            submitted_to,
            submission_result,
        )

    @classmethod
    def _from_list(cls, obj: list[dict]) -> list['NotificationSubmissionState']:
        return [cls._from_dict(i) for i in obj]


@dataclass
class NotificationErrorSolution:
    """Reasons for why the error might occur and steps to take to resolve it."""

    error_reason: str | None
    error_solution: str | None

    @classmethod
    def _from_list(cls, obj: list[dict]) -> list['NotificationErrorSolution']:
        return [cls(i['errorReason'], i['errorSolution']) for i in obj]
