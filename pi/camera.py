import io
import logging

import picamera
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import utils as utils
from classifier import Classifier

LABEL_PATH = "labels.txt"
MODEL_PATH = "../tflite_model/model_float16.tflite"
TOP_NUM = 1
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 380
CAMERA_RESOLUTION = (CAMERA_WIDTH, CAMERA_HEIGHT)
THRESHOLD = 0.8
FONT = ImageFont.truetype("DejaVuSans.ttf", 48)


def main():
    classifier = Classifier(MODEL_PATH, LABEL_PATH)
    overlay = None
    with picamera.PiCamera(resolution=CAMERA_RESOLUTION, framerate=30) as camera:
        camera.start_preview()
        try:
            stream = io.BytesIO()
            for _ in camera.capture_continuous(stream, format='jpeg', use_video_port=True):
                stream.seek(0)
                image = Image.open(stream).convert('RGB')
                image_data = utils.preprocess(image, classifier.input_size)
                result = classifier.classify(image_data, TOP_NUM)

                output = ""
                for label, confidence in result.items():
                    if confidence < THRESHOLD:
                        break
                    output += "{}({:.4f})".format(label, confidence)
                print(output, end='\r')

                o = add_text_overlay(camera, output)
                if overlay is not None:
                    camera.remove_overlay(overlay)
                overlay = o

                stream.seek(0)
                stream.truncate()

        finally:
            camera.stop_preview()


def add_text_overlay(camera, text):
    img = Image.new('RGBA', CAMERA_RESOLUTION, (255, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rectangle(((208, 68), (432, 292)))
    draw.text((0, CAMERA_HEIGHT - 50), text, fill='white', font=FONT)
    pad = Image.new('RGBA', (((img.size[0] + 31) // 32) * 32, ((img.size[1] + 15) // 16) * 16))
    pad.paste(img, (0, 0))
    o = camera.add_overlay(pad.tobytes(), size=img.size)
    o.alpha = 128
    o.layer = 3
    return o


if __name__ == '__main__':
    logging.basicConfig(level=logging.WARN, format='%(levelname)s: %(message)s')
    logger = logging.getLogger(__name__)
    main()
