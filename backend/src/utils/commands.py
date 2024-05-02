from transform_images import rename_pics, resize_pics, save_cut_pics, to_jpg
from src.utils.paths import f_path_non_erotic, dest_path_resized_non_erotic, dest_path_cut_non_erotic, \

to_jpg(f_path_non_erotic)
to_jpg(f_path_erotic)
to_jpg(f_path_porn)

rename_pics(f_path_non_erotic, 'non-erotic')
rename_pics(f_path_erotic, 'erotic')
rename_pics(f_path_porn, 'pornographic')

resize_pics(f_path_non_erotic, dest_path_resized_non_erotic, 100)
resize_pics(f_path_erotic, dest_path_resized_erotic, 100)
resize_pics(f_path_porn, dest_path_resized_porn, 100)

save_cut_pics(f_path_non_erotic, dest_path_cut_non_erotic, 3)
save_cut_pics(f_path_erotic, dest_path_cut_erotic, 3)
save_cut_pics(f_path_porn, dest_path_cut_porn, 3)
