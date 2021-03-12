import base64
import filetype
import io
import json
import requests
import time

from google.cloud import vision_v1
from google.cloud.vision_v1 import enums
from google.protobuf.json_format import MessageToDict, MessageToJson
from log_config import *

logger = get_logger(__name__)

vision_client = vision_v1.ImageAnnotatorClient()
def annotate_image_url(url):

    source = {"image_uri": url}
    image = {"source": source}
    features = [
        {"type": enums.Feature.Type.CROP_HINTS},
        {"type": enums.Feature.Type.TEXT_DETECTION},
        {"type": enums.Feature.Type.IMAGE_PROPERTIES},
    ]
    cropHintsParams = {"aspect_ratios": [1.77]}
    imageContext = {"crop_hints_params": cropHintsParams}
    request = {"image": image, "features": features, "image_context": imageContext}
    response = vision_client.annotate_image(request)
    repsonseJson = MessageToJson(response)
    logger.debug(repsonseJson)

    return MessageToDict(response)
