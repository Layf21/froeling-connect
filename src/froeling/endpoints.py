LOGIN = 'https://connect-api.froeling.com/connect/v1.0/resources/login'
# post data: {"username": username, "password": password}

FACILITY = 'https://connect-api.froeling.com/connect/v1.0/resources/service/user/{}/facility'
# 1: user_id
# facility_ids = res[*]["facilityId"]

OVERVIEW = 'https://connect-api.froeling.com/fcs/v1.0/resources/user/{}/facility/{}/overview'
# 1: user_id 2: facility_id

COMPONENT_LIST = 'https://connect-api.froeling.com/fcs/v1.0/resources/user/{}/facility/{}/componentList'
# 1: user_id 2: facility_id

COMPONENT = 'https://connect-api.froeling.com/fcs/v1.0/resources/user/{}/facility/{}/component/{}'
# 1: user_id  2: facility_id  3: component_id

NOTIFICATION_LIST = 'https://connect-api.froeling.com/connect/v1.0/resources/service/user/{}/notification'
# 1: user_id

NOTIFICATION = 'https://connect-api.froeling.com/connect/v1.0/resources/service/user/{}/notification/{}'
# 1: user_id  2: notification_id
