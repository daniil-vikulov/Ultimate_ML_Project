import pathlib
import os

f_path_non_erotic = pathlib.Path("../../data/train/non-erotic")
dest_path_resized_non_erotic = pathlib.Path("../../data/train/non-erotic/non-erotic_resized")
if not os.path.exists(dest_path_resized_non_erotic):
    os.makedirs(dest_path_resized_non_erotic)
dest_path_cut_non_erotic = pathlib.Path("../../data/train/non-erotic/non-erotic_cut")
if not os.path.exists(dest_path_cut_non_erotic):
    os.makedirs(dest_path_cut_non_erotic)
f_path_erotic = pathlib.Path("../../data/train/erotic")
dest_path_resized_erotic = pathlib.Path("../../data/train/erotic/erotic_resized")
if not os.path.exists(dest_path_resized_erotic):
    os.makedirs(dest_path_resized_erotic)
dest_path_cut_erotic = pathlib.Path("../../data/train/erotic/erotic_cut")
if not os.path.exists(dest_path_cut_erotic):
    os.makedirs(dest_path_cut_erotic)
f_path_porn = pathlib.Path("../../data/train/pornographic")
dest_path_resized_porn = pathlib.Path("../../data/train/pornographic/pornographic_resized")
if not os.path.exists(dest_path_resized_porn):
    os.makedirs(dest_path_resized_porn)
dest_path_cut_porn = pathlib.Path("../../data/train/pornographic/pornographic_cut")
if not os.path.exists(dest_path_cut_porn):
    os.makedirs(dest_path_cut_porn)
