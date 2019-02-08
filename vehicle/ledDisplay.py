import time
import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306 as fruit
import RPi.GPIO as GPIO
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import _thread



class User2VehicleInterface:

    def __init__(self,I2C,batIP,ethernetIP,wirelessIP):

        self.fontPath = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
        self.disp = fruit.SSD1306_128_32(rst=24, i2c_address=I2C)
        self.width = self.disp.width
        self.height = self.disp.height
        self.image = Image.new('1', (self.width, self.height))
        self.draw = ImageDraw.Draw(self.image)
        self.font = ImageFont.truetype(self.fontPath, 20)

        self.disp.begin()
        self.disp.clear()
        self.disp.display()
        self.draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)
        self.loadFlag = True
        self.currentlyLoading = False
        self.messages={"connecting2FC" : [["Initializing",(12,0,0,0)],["flight controller...",(12,1,0,0)]]}


    def connectingToFC(self):
        for m in self.messages["connecting2FC"]:
            self.drawText(m[0], m[1])
        self.displayText()
        _thread.start_new_thread(self.loading,("connecting2FC",))



    def drawText(self, text, dims):
        size, line, offset, yoff = dims
        font = ImageFont.truetype(self.fontPath, size)
        self.draw.text((offset, line*size + yoff), text, font=font, fill=1)

    def displayText(self):
        self.disp.image(self.image)
        self.disp.display()
        time.sleep(.01)

    def loading(self, prevText):

        offset=0
        sign = 1
        while self.loadFlag:
            self.draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)
            for m in self.messages[prevText]:
                self.drawText(m[0], m[1])
            self.drawText("...", (12, 2, offset,-2))
            self.displayText()
            time.sleep(.5)
            offset += 8 * sign
            if offset >= 106:
                sign = -1
            elif offset <= 0:
                sign = 1

    def main(self):
        pass



if __name__ == '__main__':


    ui = User2VehicleInterface(I2C=0x3C)
    ui.connectingToFC()

    try:
        tic = time.time()
        print("startuing")
        while True:
            if time.time() - tic >= 10:
                ui.loadFlag = False
                break

    except KeyboardInterrupt:
        GPIO.cleanup()
