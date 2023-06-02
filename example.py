import asyncio
import logging

from froeling import Froeling

username = input('Username (E-Mail): ')
password = input('Password         : ')


def print_new_token(token):  # Gets executed when a new token was created (useful for storing the token for next time the program is run)
    print('The new token ist:', token)


async def main():
    logging.basicConfig(level=logging.INFO)

    async with Froeling(username, password, auto_reauth=True, token_callback=print_new_token) as client:
        #client.session.debug = True  # Print all requests and responses

        await client.login()  # Generate new token with username anb password

        await client.get_notifications()  # Fetch notifications
        notification = client.notifications[0]
        await notification.info()  # Get more notification info of one of the notifications
        print(f'{notification.notification_id} Unread: {notification.unread}\n{notification.body}')

        await client.get_facilities()  # Get a list of all facilities
        facility = list(client.facilities.values())[0]

        await facility.get_components()  # Get all components of the facility
        example_component = list(facility.components.values())[0]
        await example_component.get_data()  # Get more information about the component
        print(f'{example_component.type} {example_component.sub_type}: {example_component.display_name} \n{"_" * 20}')
        for i in example_component.datapoints:  # Loop over all data af the component
            print(i.display_name, ":", i.get())


asyncio.get_event_loop().run_until_complete(main())
