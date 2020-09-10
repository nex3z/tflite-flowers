import logging
import time
from collections import OrderedDict

import numpy as np
from tflite_runtime.interpreter import Interpreter

logger = logging.getLogger(__name__)


class Classifier(object):
    def __init__(self, model_path, label_path):
        self.interpreter = Interpreter(model_path=model_path)
        self.interpreter.allocate_tensors()
        self.labels = load_labels(label_path)

        self.input_details = self.interpreter.get_input_details()[0]
        self.input_scale, self.input_zero_point = self.input_details['quantization']
        self.input_tensor = self.input_details['index']

        input_shape = self.input_details['shape']
        self.input_size = tuple(input_shape[:2] if len(input_shape) == 3 else input_shape[1:3])

        self.output_details = self.interpreter.get_output_details()[0]
        self.output_scale, self.output_zero_point = self.output_details['quantization']
        self.output_tensor = self.output_details['index']

        logger.info(f"Loaded model {model_path}")
        logger.info(f"[Input] dtype: {self.input_details['dtype']}, scale: {self.input_scale}, "
                    f"zero_point: {self.input_zero_point}")
        logger.info(f"[Output] dtype: {self.output_details['dtype']}, scale: {self.output_scale}, "
                    f"zero_point: {self.output_zero_point}")

    def classify(self, image, top=5):
        if len(image.shape) < 4:
            image = np.expand_dims(image, axis=0)

        if self.input_details['dtype'] == np.uint8:
            image = image / self.input_scale + self.input_zero_point

        start_time = time.time()

        self.interpreter.set_tensor(self.input_tensor, image)
        self.interpreter.invoke()
        output = self.interpreter.get_tensor(self.output_tensor)[0]

        elapsed = time.time() - start_time
        logger.info("Elapsed {:.6f}s".format(elapsed))

        if self.output_details['dtype'] == np.uint8:
            output = self.output_scale * (output - self.output_zero_point)

        top_k_idx = np.argsort(output)[::-1][:top]
        result = OrderedDict()
        for idx in top_k_idx:
            result[self.labels[idx]] = output[idx]

        return result


def load_labels(label_path):
    with open(label_path, 'r') as f:
        labels = list(map(str.strip, f.readlines()))
    return labels
