import asyncio
import logging
from dotenv import load_dotenv
import os

from froeling import Froeling

load_dotenv()
username = os.getenv('USERNAME')
password = os.getenv('PASSWORD')
token = os.getenv('TOKEN')

if not (username and password):
    username = input('Username (E-Mail): ')
    password = input('Password         : ')


def print_new_token(
    token,
):  # Gets executed when a new token was created (useful for storing the token for next time the program is run)
    print('The new token ist:', token)


async def main():
    # You can use an external logger
    logging.basicConfig(level=logging.INFO)

    # When only using token, auto reauth is not available
    async with Froeling(
        username,
        password,
        token=token,
        auto_reauth=True,
        language='en',
        token_callback=print_new_token,
    ) as client:
        for notification in (await client.get_notifications())[:3]:  # Fetch notifications
            await (
                notification.info()
            )  # Load more information about one of the notifications
            print(
                f'\n[Notification {notification.id}] Subject: {notification.subject}\n{notification.details.body}\n\n'
            )

        facility = (await client.get_facilities())[0]  # Get a list of all facilities
        print(facility)

        # Get all components of the facility
        example_component = (await facility.get_components())[0]
        print(example_component)

        await (
            example_component.update()
        )  # Get more information about the component. This includes the parameters.
        print(f'{example_component.type} {example_component.sub_type}: {example_component.display_name} \n{"_" * 20}')
        for parameter in (
            example_component.parameters.values()
        ):  # Loop over all data af the component
            print(parameter.display_name, ':', parameter.display_value)

        # You can directly reference a component of a facility by its id
        example_component2 = facility.get_component('1_100')
        await example_component2.update()  # The update method is required to fully populete the component's data.
        print('\n\nExample Component:', example_component2.display_name)

        param = example_component2.parameters.get('7_28')
        if param:
            print(f'Value was {param.display_value}')
            print(f'Setting {param.display_name} to 80')
            # await param.set_value(80) # This changes a live system parameter. Uncomment only if you understand the effect.

        # If you know the facilityId and component_id, you can get the component like this. The data won't be populated.
        client.get_component(facility.facility_id, '1_100')


asyncio.run(main())
