import asyncio
import logging
from dotenv import load_dotenv
import os

from froeling import Froeling

load_dotenv()
username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")
token = os.getenv("TOKEN")

if not (username and password):
    username = input('Username (E-Mail): ')
    password = input('Password         : ')


def print_new_token(token):  # Gets executed when a new token was created (useful for storing the token for next time the program is run)
    print('The new token ist:', token)



async def main():
    # You can use an external logger
    logging.basicConfig(level=logging.INFO)

    # When only using token, auto reauth is not available
    async with Froeling(username, password, token=token, auto_reauth=True, language='en', token_callback=print_new_token) as client:

        for notification in await client.get_notifications():  # Fetch notifications
            await notification.info()  # Load more information about one of the notifications
            print(f'\n[Notification {notification.id}] Subject: {notification.subject}\n{notification.details.body}\n\n')


        facility = (await client.get_facilities())[0]  # Get a list of all facilities
        print(facility)

        example_component = (await facility.get_components())[0]  # Get all components of the facility
        print(example_component)

        await example_component.update()  # Get more information about the component. This includes the parameters.
        print(f'{example_component.type} {example_component.sub_type}: {example_component.display_name} \n{"_" * 20}')
        for i in example_component.parameters:  # Loop over all data af the component
            print(i.display_name, ":", i.display_value)


        # You can directly reference a component of a facility by its id
        example_component2 = facility.get_component("1_100")
        await example_component2.update()
        print("\n\nExample Component:", example_component2.display_name)

        for param in example_component2.parameters:
            if param.id == "7_28":
                print(f"Setting {param.display_name} to 80")
                # await param.set_value(80)


        # If you know the facility_id and component_id, you can get the component like this.
        client.get_component(facility.facility_id, "1_100")


asyncio.get_event_loop().run_until_complete(main())
