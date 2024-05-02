from PIL import Image
import os


def to_jpg(file_path):
    for file_name in os.listdir(file_path):
        full_path = os.path.join(file_path, file_name)
        if os.path.isfile(full_path) and not file_name.startswith('.'):
            if file_name.endswith('jpg'):
                continue
            else:
                img_path = os.path.join(file_path, file_name)
                try:
                    img = Image.open(img_path)
                    if img.mode == 'RGBA':
                        img = img.convert('RGB')
                    new_path = os.path.join(file_path, file_name.split('.')[0] + '.jpg')
                    img.save(new_path, 'JPEG')
                    os.remove(img_path)
                except Exception as e:
                    print(f"impossible to reformat the file {file_name}: {e}")
        elif os.path.isdir(full_path):
            continue


def rename_pics(file_path, name):
    for i, path in enumerate(file_path.glob('*.jpg')):
        new_name = name + str(i) + path.suffix
        path.rename(file_path / new_name)


def resize_pics(file_path, dest, new_size):
    for file_name in os.listdir(file_path):
        if file_name.endswith('.jpg'):
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
        if filename.endswith('.jpg'):
            img_path = os.path.join(file_path, filename)
            img = Image.open(img_path)
            cropped_images = cut_pics(img, m)
            for idx, cropped_img in enumerate(cropped_images):
                new_filename = f"{filename.split('.')[0]}_cut_{idx}.{filename.split('.')[1]}"
                new_img_path = os.path.join(dest, new_filename)
                cropped_img.save(new_img_path)
