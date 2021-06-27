import tonemap_and_bloom as tb
from timeit import timeit
import cv2 as cv

name = "mountain"
evs = [-1, 0, 1]
ext = "jpg"

kern_size = (55, 55)

num = 100

kernel = cv.imread("img/_flares/unreal1.jpg").astype('float64')

imgs = tb.get_images(name, evs, ext)

tone_mapped = tb.tone_mapping(imgs, 1, 1, 1)
bloom_overlay = tb.bloom(imgs[0], kernel, 2, kern_size)

print(imgs[0].shape[1], "x", imgs[0].shape[0], "x", len(evs))
print(kern_size[0], "x", kern_size[1])

tonemap = timeit(lambda: tb.tone_mapping(imgs, 1.0, 1.0, 1.0), number=num)

tonemap /= num
print("tonem: ", tonemap)

bloom = timeit(lambda: tb.bloom(imgs[0], kernel, 2.0, kern_size), number=num)

bloom /= num
print("bloom: ", bloom)

merge = timeit(lambda: tb.merge(tone_mapped, bloom_overlay, 1), number=num)

merge /= num
print("merge: ", merge)

total = timeit(lambda: tb.tonemap_and_bloom(
    imgs=imgs,
    kernel=kernel,
    contrast_weight=1.0,
    saturation_weight=1.0,
    exposure_weight=1.0,
    bloom_kernel_size=kern_size,
    smoothing_factor=2.0,
    bloom_intensity=1.0
), number=num)


total /= num

print("total: ", total)
print("calcu: ", tonemap+bloom+merge)
