import io
import logging
import sys
import picamera
from PIL import Image
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import utils as utils
from classifier import Classifier

LABEL_PATH = 'labels.txt'
MODEL_PATH = "../tflite_model/mobilenet_v2/model_float16.tflite"
TOP_NUM = 1
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 380
CAMERA_RESOLUTION = (CAMERA_WIDTH, CAMERA_HEIGHT)
THRESHOLD = 0.9


def main():
    classifier = Classifier(MODEL_PATH, LABEL_PATH)
    font = ImageFont.truetype("DejaVuSans.ttf", 48)
    overlay = None
    with picamera.PiCamera(resolution=CAMERA_RESOLUTION, framerate=30) as camera:
        camera.start_preview()
        try:
            stream = io.BytesIO()
            for _ in camera.capture_continuous(stream, format='jpeg', use_video_port=True):
                stream.seek(0)
                image = Image.open(stream).convert('RGB')
                image = utils.center_crop(image)
                image_data = utils.preprocess(image, classifier.input_size)
                result = classifier.classify(image_data, TOP_NUM)

                output = ""
                for label, prob in result.items():
                    if prob < THRESHOLD:
                        break;
                    output += "{}".format(label)
                print(output, end='\r')

                img = Image.new('RGBA', CAMERA_RESOLUTION, (255, 0, 0, 0))
                draw = ImageDraw.Draw(img)
                draw.rectangle(((208, 68), (432, 292)))
                draw.text((0, CAMERA_HEIGHT-50), output, fill='white', font=font)
                pad = Image.new('RGBA', (
                    ((img.size[0] + 31) // 32) * 32,
                    ((img.size[1] + 15) // 16) * 16,
                ))
                pad.paste(img, (0, 0))

                o = camera.add_overlay(pad.tobytes(), size=img.size)
                o.alpha = 128
                o.layer = 3

                if overlay is not None:
                    camera.remove_overlay(overlay)
                overlay = o

                stream.seek(0)
                stream.truncate()

        finally:
            camera.stop_preview()


if __name__ == '__main__':
    logging.basicConfig(level=logging.WARN, format='%(levelname)s: %(message)s')
    logger = logging.getLogger(__name__)
    main()
