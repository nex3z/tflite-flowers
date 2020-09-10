import argparse
import logging

from PIL import Image

import utils as utils
from classifier import Classifier

LABEL_PATH = "labels.txt"
MODEL_PATH = "../tflite_model/model_float16.tflite"
TOP_NUM = 5


def main():
    parser = build_arg_parser()
    args = parser.parse_args()

    classifier = Classifier(MODEL_PATH, LABEL_PATH)
    image = Image.open(args.image_file).convert('RGB')
    image_data = utils.preprocess(image, classifier.input_size)
    result = classifier.classify(image_data, TOP_NUM)

    for label, prob in result.items():
        print(label, prob)


def build_arg_parser():
    parser = argparse.ArgumentParser(description='Image Classification')
    parser.add_argument('-f', dest='image_file', type=str, help='Image file', required=True)
    return parser


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    logger = logging.getLogger(__name__)
    main()
