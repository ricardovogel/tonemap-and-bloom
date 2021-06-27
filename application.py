from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty
import tonemap_and_bloom as tb
import cv2 as cv


class ImgView(BoxLayout):
    pass


class BloomApp(App):
    def run_process(self, namestr, evsstr, extstr, kernelstr, tonemapstr, kernsizestr, smoothingstr, intensitystr):
        print("running...", namestr, evsstr, extstr, kernelstr,
              tonemapstr, kernsizestr, smoothingstr, intensitystr)
        try:
            (merged_final, tone_mapped, bloom_overlay) = tb.tonemap_and_bloom(
                imgs=tb.get_images(
                    namestr, list(map(lambda x: int(x) if int(x) == float(x) else float(x), evsstr.split(","))), extstr),
                kernel=cv.imread("img/_flares/" + kernelstr).astype('float64'),
                contrast_weight=float(tonemapstr.split(",")[0]),
                saturation_weight=float(tonemapstr.split(",")[1]),
                exposure_weight=float(tonemapstr.split(",")[2]),
                bloom_kernel_size=(int(kernsizestr.split(
                    ",")[0]), int(kernsizestr.split(",")[1])),
                smoothing_factor=float(smoothingstr),
                bloom_intensity=float(intensitystr)
            )
            tb.save_image(bloom_overlay, "img/app_output/bloom_overlay.png")
            tb.save_image(tone_mapped, "img/app_output/tone_mapped.png")
            tb.save_image(merged_final, "img/app_output/final.png")
            print("completed!")
        except:
            print("Something went wrong!")

    def build(self):
        return ImgView()


if __name__ == '__main__':
    BloomApp().run()
