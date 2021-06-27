import tonemap_and_bloom as tb
import cv2 as cv
import time
import numpy as np

# Type hint
Image = np.ndarray

name = "monument"
evs = [-4, -2, 2, 4]
ext = "png"
# name = "mountain"
# evs = [-1, 0, 1]
# ext = "jpg"
# name = "delftlights"
# evs = [-2, -1, 0, 1, 2]
# ext = "jpg"
# name = "fairy"
# evs = [-2, -1, 0, 1, 2]
# ext = "jpg"
# name = "window"
# evs = [-6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5]
# ext = "jpg"

kernel = cv.imread("img/_kernels/unreal.jpg").astype('float64')

imgs = tb.get_images(name, evs, ext)

start_time = time.time()

(merged_final, tone_mapped, bloom_overlay) = tb.tonemap_and_bloom(
    imgs=imgs,
    kernel=kernel,
    contrast_weight=1.0,
    saturation_weight=1.0,
    exposure_weight=1.0,
    bloom_kernel_size=(25, 25),
    smoothing_factor=1.0,
    bloom_intensity=1.0,
    # use_gaussian_bloom=True,                          # Optional setting
    # threshold=200,                                    # Optional setting
    # bloom_image=tb.tone_mapping(imgs, 1.0, 1.0, 1.0), # Optional setting
)

stop_time = time.time()
final_time = stop_time - start_time
print("time: ", final_time)

# Save Images
ext = "png"
tb.save_image(bloom_overlay, "img/{}/output/{}.{}".format(name, "bloom", ext))
tb.save_image(
    tone_mapped, "img/{}/output/{}.{}".format(name, "tone_mapped", ext))
tb.save_image(
    merged_final, "img/{}/output/{}.{}".format(name, "final_edited", ext))
