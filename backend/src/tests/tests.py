import tensorflow as tf


def print_greeting():
    print('Hello world')


def check_tensorflow():
    gpus = tf.config.list_physical_devices('GPU')
    if not gpus:
        raise RuntimeError(
            'No GPU found! Make sure TensorFlow is installed with GPU support and the GPU is properly configured.')
    for gpu in gpus:
        print(f"GPU found: {gpu}")
    try:
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
        logical_gpus = tf.config.list_logical_devices('GPU')
        print(f"{len(gpus)} Physical GPUs, {len(logical_gpus)} Logical GPU")
    except RuntimeError as e:
        print(e)
