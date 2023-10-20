import base64
from glob import glob
from io import BytesIO
from os import path
from pickle import dump

import numpy as np
from PIL import Image


def preprocess_image_file(image_path):
    image = Image.open(image_path)
    return _transform(image)


def preprocess_encoded_image(base64encoded_image):
    img_bytes = base64.decodebytes(base64encoded_image.encode())
    image = Image.open(BytesIO(img_bytes))
    return _transform(image)


def preprocess_image_folder(data_folder='./data'):
    print('Commencing data preprocessing.')

    image_names, image_file_paths = _scan_images_folder(data_folder)

    image_data = [
        preprocess_image_file(image_path) for image_path in image_file_paths
    ]
    with open(f'{data_folder}/images.pickle', 'wb') as outputfile:
        dump([image_names, image_data], outputfile)

    print('Data preprocessing done.')


def _scan_images_folder(images_folder):
    print(f'Scanning images folder {images_folder}.')

    image_file_paths = glob(path.join(images_folder, "*.jpg"))
    image_names = [
        file_path.split('/')[-1].rstrip('.jpg')
        for file_path in image_file_paths
    ]
    return image_names, image_file_paths


def _transform(image):
    model_image_size = (416, 416)
    boxed_image = _letterbox_image(image, tuple(reversed(model_image_size)))
    image_data = np.array(boxed_image, dtype='float32')
    image_data /= 255.
    image_data = np.transpose(image_data, [2, 0, 1])
    image_data = np.expand_dims(image_data, 0)
    return image_data


def _letterbox_image(image, size):
    '''resize image with unchanged aspect ratio using padding'''
    iw, ih = image.size
    w, h = size
    scale = min(w/iw, h/ih)
    nw = int(iw*scale)
    nh = int(ih*scale)

    image = image.resize((nw, nh), Image.BICUBIC)
    new_image = Image.new('RGB', size, (128, 128, 128))
    new_image.paste(image, ((w-nw)//2, (h-nh)//2))
    return new_image


if __name__ == '__main__':
    preprocess_image_folder(data_folder='/data')
