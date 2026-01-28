import asyncio
from io import BytesIO
from pathlib import Path

from task._models.custom_content import Attachment, CustomContent
from task._utils.constants import API_KEY, DIAL_URL, DIAL_CHAT_COMPLETIONS_ENDPOINT
from task._utils.bucket_client import DialBucketClient
from task._utils.model_client import DialModelClient
from task._models.message import Message
from task._models.role import Role


async def _put_image() -> Attachment:
    file_name = 'dialx-banner.png'
    image_path = Path(__file__).parent.parent.parent / file_name
    mime_type_png = 'image/png'

     #  1. Create DialBucketClient
    async with DialBucketClient(API_KEY, DIAL_URL) as dial_bucket_client:
        # Image details
        file_name = 'dialx-banner.png'
        image_path = Path(__file__).parent.parent.parent / file_name
        mime_type_png = 'image/png'

        #  2. Open image file
        with open(image_path, "rb") as file:
            #  3. Use BytesIO to load bytes of image
            image_bytes = BytesIO(file.read())

        #  4. Upload file with client
        response = await dial_bucket_client.put_file(
            name=file_name, mime_type=mime_type_png, content=image_bytes
        )
        uploaded_url = response.get('url')

        #  5. Return Attachment object with title (file name), url and type (mime type)
        return Attachment(title=file_name, url=uploaded_url, type=mime_type_png)


async def start() -> None:
    #  1. Create DialModelClient
    dial_model_client = DialModelClient(DIAL_CHAT_COMPLETIONS_ENDPOINT, "gpt-4o", API_KEY)

    #  2. Upload image
    image = await _put_image()

    #  3. Print attachment to see result
    print(f"Uploaded image: {image}")

    #  4. Call chat completion via client with list containing one Message
    dial_model_client.get_completion([Message(
        Role.USER,
        "What do you see on this picture?",
        CustomContent([image])
    )])

asyncio.run(start())
