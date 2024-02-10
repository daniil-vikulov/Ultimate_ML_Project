import pathlib
import shutil

from PIL import Image
import os
f_path = pathlib.Path("/Users/elizabeth/PycharmProjects/Ultimate_ML_Project/data/train/non-erotic")
dest_path_resized = pathlib.Path("/Users/elizabeth/PycharmProjects/Ultimate_ML_Project/data/train/non-erotic/non-erotic_resized")
if not os.path.exists(dest_path_resized):
    os.makedirs(dest_path_resized)
dest_path_cut = pathlib.Path("/Users/elizabeth/PycharmProjects/Ultimate_ML_Project/data/train/non-erotic/non-erotic_cut")
if not os.path.exists(dest_path_cut):
    os.makedirs(dest_path_cut)
f_path_erotic = pathlib.Path("/Users/elizabeth/PycharmProjects/Ultimate_ML_Project/data/train/erotic")
dest_path_resized_erotic = pathlib.Path("/Users/elizabeth/PycharmProjects/Ultimate_ML_Project/data/train/erotic/erotic_resized")
if not os.path.exists(dest_path_resized_erotic):
    os.makedirs(dest_path_resized_erotic)
dest_path_cut_erotic = pathlib.Path("/Users/elizabeth/PycharmProjects/Ultimate_ML_Project/data/train/erotic/erotic_cut")
if not os.path.exists(dest_path_cut_erotic):
    os.makedirs(dest_path_cut_erotic)


def rename_pics(file_path, name):
    n = 0
    k = 0
    for i, path in enumerate(file_path.glob('*.jpg')):
        new_name = name + str(i) + path.suffix
        path.rename(file_path / new_name)
        n = i
    for i, path in enumerate(file_path.glob('*.JPG')):
        new_name = name + str(n + i + 1) + path.suffix
        path.rename(file_path / new_name)
        k = n + i + 1
    for i, path in enumerate(file_path.glob('*.png')):
        new_name = name + str(k + i + 1) + path.suffix
        path.rename(file_path / new_name)


rename_pics(f_path_erotic, 'erotic')


def resize_pics(file_path, dest, new_size):
    for file_name in os.listdir(file_path):
        if file_name.endswith('.jpg') or file_name.endswith('.png') or file_name.endswith('.JPG'):
            img_path = os.path.join(file_path, file_name)
            img = Image.open(img_path)
            (width, height) = img.size
            k = width / height
            if k == 1:
                img_resized = img.resize((new_size, new_size))
            elif k > 1:
                img_resized = img.resize((new_size, int(new_size / k)))
            else:
                img_resized = img.resize((int(k * new_size), new_size))
            new_file_name = 'resized_' + file_name
            new_img_path = os.path.join(dest, new_file_name)
            img_resized.save(new_img_path)
            # for filename in os.listdir(dest_path):
            #     img_path = os.path.join(dest_path, filename)
            #     img = Image.open(img_path)
            #     print(img.size)


# resize_pics(f_path, dest_path_resized, 100)


def cut_pics(image, m):
    width, height = image.size
    min_dim = min(width, height)
    step = min_dim // m
    cropped_images = []
    for i in range(m):
        for j in range(m):
            box = (j * step, i * step, (j + 1) * step, (i + 1) * step)
            cropped_img = image.crop(box)
            cropped_images.append(cropped_img)

    return cropped_images


def save_cut_pics(file_path, dest, m):
    for filename in os.listdir(file_path):
        if filename.endswith('.jpg') or filename.endswith('.png') or filename.endswith('.JPG'):
            img_path = os.path.join(file_path, filename)
            img = Image.open(img_path)

            cropped_images = cut_pics(img, m)

            for idx, cropped_img in enumerate(cropped_images):
                new_filename = f"{filename.split('.')[0]}_cut_{idx}.{filename.split('.')[1]}"
                new_img_path = os.path.join(dest, new_filename)

                cropped_img.save(new_img_path)

            # print(f"Изображение {filename} разрезано на {m*m} фрагментов и сохранено")


# save_cut_pics(f_path, dest_path_cut, 3)


