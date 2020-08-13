import glob
import math
import os
from shutil import copyfile

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import tensorflow as tf
from PIL import Image
from sklearn.model_selection import StratifiedShuffleSplit
from tqdm import tqdm


def read_dir(data_dir):
    files = []
    for file_path in glob.glob(f"{data_dir}/*/*.*"):
        class_name = os.path.basename(os.path.dirname(file_path))
        files.append({'class': class_name, 'file_path': file_path})
    df_data = pd.DataFrame(files)
    return df_data


def stratified_split(df_data, test_size, random_seed=47):
    split = StratifiedShuffleSplit(n_splits=1, test_size=test_size, random_state=random_seed)
    df_train, df_test = None, None
    for train_idx, test_idx in split.split(df_data, df_data['class']):
        df_train = df_data.loc[train_idx]
        df_test = df_data.loc[test_idx]

    return df_train, df_test


def copy_images(df, base_dir):
    os.makedirs(base_dir, exist_ok=True)
    for idx, row in tqdm(df.iterrows(), total=len(df), ascii=True):
        class_name = row['class']
        src_path = row['file_path']
        category_path = os.path.join(base_dir, class_name)
        os.makedirs(category_path, exist_ok=True)
        dst_path = os.path.join(category_path, os.path.basename(src_path))
        copyfile(src_path, dst_path)


def plot_images(df_data, num_col=4):
    df_data = df_data.reset_index(drop=True)
    df_data['file_name'] = df_data['file_path'].apply(os.path.basename)

    num_row = math.ceil(len(df_data) / num_col)
    plt.figure(figsize=(4 * num_col, 4 * num_row))
    for idx, row in df_data.iterrows():
        plt.subplot(num_row, num_col, idx + 1)
        path = row['file_path']
        img = Image.open(path)
        plt.imshow(img)
        plt.title("\n".join([f"{key}: {value}" for key, value in row.iteritems() if key != 'file_path']))
        plt.axis('off')

    plt.tight_layout()
    plt.show()


def evaluate(model, val_iter):
    result = model.predict(val_iter)
    y_hat = np.argmax(result, axis=1)
    y = val_iter.classes

    df_result = pd.DataFrame({'y': y, 'y_hat': y_hat, 'file_path': val_iter.filepaths})
    df_result['correct'] = df_result['y'] == df_result['y_hat']

    df_acc = df_result.loc[df_result['y'] == df_result['y_hat'], ]
    accuracy = len(df_acc) / len(df_result)
    print("accuracy = {:.4f}".format(accuracy))

    return df_result


def evaluate_tflite_model(model_path, val_iter):
    interpreter = tf.lite.Interpreter(model_path=model_path)
    interpreter.allocate_tensors()
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    count, acc = 0, 0
    loop = tqdm(val_iter, ascii=True)
    for i, (data, label) in enumerate(loop):
        if i == len(val_iter):
            break

        interpreter.set_tensor(input_details[0]['index'], data)
        interpreter.invoke()
        predictions = interpreter.get_tensor(output_details[0]['index'])

        count += 1
        if np.argmax(predictions) == np.argmax(label):
            acc += 1
        loop.set_postfix(acc="{:.4f}".format(acc / count))

    loop.close()
    return acc / count
