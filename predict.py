import io
import time
import sys
import numpy as np
import platform
from PIL import ImageFont, ImageDraw, Image
from matplotlib import pyplot as plt
import os
from models import Character

import cv2
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from msrest.authentication import CognitiveServicesCredentials

class Predict:

    SUBSCRIPTION_KEY = "d48cd6f2811c4605a71e222105fe7c7c"
    ENDPOINT_URL = "https://asure-ocr-checkmate.cognitiveservices.azure.com/"
    computervision_client = ComputerVisionClient(ENDPOINT_URL, CognitiveServicesCredentials(SUBSCRIPTION_KEY))

    def __init__(self, filename=None):
        self.filename = filename
        self.character_info = None
        self.job_info = None

    def api(self, path):
        imageData = open(path, "rb").read()
        sbuf = io.BytesIO(imageData)
        response = self.computervision_client.read_in_stream(sbuf, raw=True)
        operationLocation = response.headers["Operation-Location"]
        operationID = operationLocation.split("/")[-1]

        while True:
            read_result = self.computervision_client.get_read_result(operationID)
            if read_result.status not in ['notStarted', 'running']:
                break
            time.sleep(1)

        if read_result.status == OperationStatusCodes.succeeded:
            img = cv2.imread(path)
            roi_img = img.copy()

            prev_topLeft = 0
            prev_topRight = 0
            prev_bottomRight = 0
            prev_bottomLeft = 0
            character_list = []
            character = None

            for text_result in read_result.analyze_result.read_results:
                for line in text_result.lines:
                    text = line.text
                    box = list(map(int, line.bounding_box))
                    (tlX, tlY, trX, trY, brX, brY, blX, blY) = box
                    pts = ((tlX, tlY), (trX, trY), (brX, brY), (blX, blY))

                    topLeft = pts[0]
                    topRight = pts[1]
                    bottomRight = pts[2]
                    bottomLeft = pts[3]

                    cv2.line(roi_img, topLeft, topRight, (0, 255, 0), 2)
                    cv2.line(roi_img, topRight, bottomRight, (0, 255, 0), 2)
                    cv2.line(roi_img, bottomRight, bottomLeft, (0, 255, 0), 2)
                    cv2.line(roi_img, bottomLeft, topLeft, (0, 255, 0), 2)
                    roi_img = put_text(roi_img, text, topLeft[0], topLeft[1] + 15, font_size=10)

                    # print(text, topLeft, topRight, bottomRight, bottomLeft)

                    self.analyze_text(text, topLeft, topRight, bottomRight, bottomLeft)

                    if self.character_info is not None:
                        if topLeft < self.character_info['top_left'] and topRight > self.character_info['top_right']:
                            character = Character()
                            character.name = text

                    if self.job_info is not None:
                        if topLeft < self.job_info['top_left'] and topRight > self.job_info['top_right']:
                            if character is None:
                                continue
                            else:
                                character.job = text
                                character_list.append(character)
                                #print(character.__dict__)
                                character = None

            if len(roi_img.shape) < 3:
                rgbImg = cv2.cvtColor(roi_img, cv2.COLOR_GRAY2RGB)
            else:
                rgbImg = cv2.cvtColor(roi_img, cv2.COLOR_BGR2RGB)

            plt.imsave(os.path.join('static', 'uploads', 'ocr_' + path.split('/')[-1]), rgbImg)

            for idx, character_ in enumerate(character_list):
                character_.id = idx + 1

        return character_list

    def analyze_text(self, text, top_left, top_right, bottom_right, bottom_left):
        if text == "캐릭터명":
            self.character_info = {
                'top_left': top_left,
                'top_right': top_right,
                'bottom_right': bottom_right,
                'bottom_left': bottom_left
            }

        if text == "직업명":
            self.job_info = {
                'top_left': top_left,
                'top_right': top_right,
                'bottom_right': bottom_right,
                'bottom_left': bottom_left
            }



def put_text(image, text, x, y, color=(0, 255, 0), font_size=22):
    if type(image) == np.ndarray:
        color_coverted = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(color_coverted)

    if platform.system() == 'Darwin':
        font = 'AppleGothic.ttf'
    elif platform.system() == 'Windows':
        font = 'malgun.ttf'

    image_font = ImageFont.truetype(font, font_size)
    font = ImageFont.load_default()
    draw = ImageDraw.Draw(image)

    draw.text((x, y), text, font=image_font, fill=color)

    numpy_image = np.array(image)
    opencv_image = cv2.cvtColor(numpy_image, cv2.COLOR_RGB2BGR)

    return opencv_image

