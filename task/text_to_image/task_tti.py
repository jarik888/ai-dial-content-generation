import asyncio
from datetime import datetime

from task._models.custom_content import Attachment
from task._utils.constants import API_KEY, DIAL_URL, DIAL_CHAT_COMPLETIONS_ENDPOINT
from task._utils.bucket_client import DialBucketClient
from task._utils.model_client import DialModelClient
from task._models.message import Message
from task._models.role import Role

class Size:
    """
    The size of the generated image.
    """
    square: str = '1024x1024'
    height_rectangle: str = '1024x1792'
    width_rectangle: str = '1792x1024'


class Style:
    """
    The style of the generated image. Must be one of vivid or natural.
     - Vivid causes the model to lean towards generating hyper-real and dramatic images.
     - Natural causes the model to produce more natural, less hyper-real looking images.
    """
    natural: str = "natural"
    vivid: str = "vivid"


class Quality:
    """
    The quality of the image that will be generated.
     - ‘hd’ creates images with finer details and greater consistency across the image.
    """
    standard: str = "standard"
    hd: str = "hd"

async def _save_images(attachments: list[Attachment]):
    # 1. Create DIAL bucket client
    async with DialBucketClient(API_KEY, DIAL_URL) as dial_bucket_client:
        # 2. Iterate through images from attachments, download them and then save locally
        for attachment in attachments:
            if attachment.url and attachment.type == "image/png":
                image_data = await dial_bucket_client.get_file(attachment.url)

                file_name = attachment.url.split("/")[-1]
                with open(file_name, "wb") as file:
                    file.write(image_data)

                # 3. Print confirmation that the image has been saved locally
                print(f"Image saved locally as {file_name}")

    print("All images have been saved successfully.")


def start() -> None:
    # 1. Create DialModelClient
    dial_model_client = DialModelClient(DIAL_CHAT_COMPLETIONS_ENDPOINT, "dall-e-3", API_KEY)

    # 2. Generate image for "Sunny day on Bali" using custom_fields for style, quality, and size
    custom_fields = {
        "style": Style.vivid,
        "quality": Quality.hd,
        "size": Size.square
    }
    response = dial_model_client.get_completion([Message(Role.USER, "Sunny day on Bali")], custom_fields=custom_fields)

    # 3. Get attachments from response's custom_content
    if response.custom_content and response.custom_content.attachments:
        attachments = response.custom_content.attachments

        # 4. Save generated images locally
        asyncio.run(_save_images(attachments))

        # 5. Confirm the task is tested with 'imagegeneration@005' model
        # Exception: HTTP 404: {"error":{"message":"Image generation failed with the following error: The imagegeneration@005 model has reached its end of life.
        # Please refer to the migration guide (https://docs.cloud.google.com/vertex-ai/generative-ai/docs/deprecations)
        # on how to migrate to a newer model.","type":"invalid_request_error","code":"404"}}
    else:
        print("No attachments found in the response.")


start()
