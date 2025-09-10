"""List of static API Endpoints."""

LOGIN = 'https://connect-api.froeling.com/connect/v1.0/resources/login'
"""post data: {"username": username, "password": password}"""

USER = 'https://connect-api.froeling.com/connect/v1.0/resources/service/user/{}'
"""1: user_id"""

FACILITY = (
    'https://connect-api.froeling.com/connect/v1.0/resources/service/user/{}/facility'
)
"""1: user_id
facility_ids = res[*]["facilityId"]"""

OVERVIEW = (
    'https://connect-api.froeling.com/fcs/v1.0/resources/user/{}/facility/{}/overview'
)
"""1: user_id 2: facility_id"""

COMPONENT_LIST = 'https://connect-api.froeling.com/fcs/v1.0/resources/user/{}/facility/{}/componentList'
"""1: user_id 2: facility_id"""

COMPONENT = 'https://connect-api.froeling.com/fcs/v1.0/resources/user/{}/facility/{}/component/{}'
"""1: user_id  2: facility_id  3: component_id"""

NOTIFICATION_COUNT = 'https://connect-api.froeling.com/connect/v1.0/resources/service/user/{}/notification/count'
"""1: user_id"""

NOTIFICATION_LIST = 'https://connect-api.froeling.com/connect/v1.0/resources/service/user/{}/notification'
"""1: user_id"""

NOTIFICATION = 'https://connect-api.froeling.com/connect/v1.0/resources/service/user/{}/notification/{}'
"""1: user_id  2: notification_id"""

SET_PARAMETER = 'https://connect-api.froeling.com/fcs/v1.0/resources/user/{}/facility/{}/parameter/{}'
"""1: user_id  2: facility_id  3: parameter_id"""
