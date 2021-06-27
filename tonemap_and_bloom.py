import numpy as np
import scipy.signal as sig
import cv2 as cv

# Type hint
Image = np.ndarray


def get_images(imgName: str, evs: [float], ext: str) -> [Image]:
    '''Gets images from img/[name]/input/[ev].[ext].'''

    img_file_names = []
    img_list = []
    for ev in evs:
        cur_name = "img/{}/input/{}.{}".format(imgName, ev, ext)
        img_file_names.append(cur_name)
        img_list.append(cv.imread(cur_name).astype('float64'))
    exposure_times = np.array(evs)
    return img_list


def save_image(img: Image, path: str) -> None:
    '''Saves an image to a certain path.'''

    cv.imwrite(path, img)


def to_255_range(img: Image) -> Image:
    '''Converts an from [0, 1] range to [0, 255].'''

    return np.clip(img * 255, 0, 255).astype('float64')


def to_0_1_range(img: Image) -> Image:
    '''Converts an from [0, 255] range to [0, 1].'''

    return np.clip(img / 255, 0, 1).astype('float64')


def tone_mapping(images: [Image], contrast_weight: float,
                 saturation_weight: float, exposure_weight: float) -> Image:
    '''Runs Mertens et al.'s Exposure Fusion on a list of images'''

    if (len(images) == 1):
        return images[0]
    mertens_0_to_1 = cv.createMergeMertens(contrast_weight,
                                           saturation_weight, exposure_weight).process(images).astype('float64')

    mertens_rescaled = to_255_range(mertens_0_to_1)
    return mertens_rescaled.astype('float64')


def smoothen(img: Image, smoothing_factor: float) -> Image:
    '''Applies smoothing to an image.'''

    smooth_img = to_0_1_range(img)
    smooth_img = smooth_img**smoothing_factor
    smooth_img = to_255_range(smooth_img)
    return smooth_img.astype('float64')


def bloom(img: Image, kernel: Image, smoothing_factor: float, kernel_size: (int, int), use_gaussian_bloom=False, threshold=-1) -> Image:
    '''Given an image and a kernel, applies smoothing to the image and convolves it with the kernel.'''

    if threshold == -1:
        smooth_img = smoothen(img, smoothing_factor)
    else:
        _, smooth_img = cv.threshold(img, threshold, 255, cv.THRESH_TOZERO)

    if use_gaussian_bloom:
        return cv.GaussianBlur(smooth_img, kernel_size, 0).astype('float64')

    if kernel_size != (-1, -1):
        kernel = cv.resize(kernel, kernel_size).astype('float64')
    kernel = to_0_1_range(kernel)

    b_kernel, g_kernel, r_kernel = cv.split(kernel)
    b_img, g_img, r_img = cv.split(smooth_img)

    r_bloom = sig.convolve(r_img, r_kernel, mode="same", method="fft")
    g_bloom = sig.convolve(g_img, g_kernel, mode="same", method="fft")
    b_bloom = sig.convolve(b_img, b_kernel, mode="same", method="fft")

    rgb_bloom = cv.merge((b_bloom, g_bloom, r_bloom))

    return rgb_bloom.astype('float64')


def merge(fused: Image, bloom_overlay: Image, bloom_intensity: float) -> Image:
    '''Merges the bloom overlay with the tone mapped image.'''

    return cv.scaleAdd(bloom_overlay, bloom_intensity, fused).astype('float64')


def tonemap_and_bloom(imgs: [Image], kernel: Image, contrast_weight: float, saturation_weight: float, exposure_weight: float, bloom_kernel_size: (int, int), smoothing_factor: float, bloom_intensity: float, use_gaussian_bloom=False, threshold=-1, bloom_image=None) -> (Image, Image, Image):
    '''Entry point for the algorithm. Takes the image with the lowest EV, performs convolution bloom, and adds it to a generated tone mapped image.'''

    if bloom_image is None:
        bloom_image = imgs[0]

    tone_mapped = tone_mapping(
        imgs, contrast_weight, saturation_weight, exposure_weight)
    bloom_overlay = bloom(bloom_image, kernel, smoothing_factor, bloom_kernel_size,
                          use_gaussian_bloom=use_gaussian_bloom, threshold=threshold)
    merged_final = merge(tone_mapped, bloom_overlay, bloom_intensity)
    return (merged_final, tone_mapped, bloom_overlay)
