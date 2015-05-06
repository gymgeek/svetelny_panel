"""svetelny panel s led paskem 
seriova komunikace s arduinem
atp.

FUNKCNI VZOREK
15 x 9 px

light (luminary) panel with led strip
serial communication with arduino
(beaglebone version)

FUNCTION SAMPLE
15 x 9 px
- first diode at left bottom corner
- odd rows (from bottom) from left to right
- even rows from right to left
- matrix numbering:
top line - 0 index
left column - 0 index

"""

from bbio import Serial2 
import time
import math
import cwiid
import random

def send_to_panel(command, answer=None, timeout=0.1): 
    """send command to panel
    command - command for sending
    answer - expected answer"""
    if Serial2.baud == 0: 
        setup()
    if answer is None: 
        answer = command
    Serial2.write(command)
    itime = time.time()
    icommand = ""
    while(icommand.count(answer)==0 and time.time() < itime + timeout):
        ichar = Serial2.read()
        if ichar != "\r": 
            icommand += ichar
    if icommand.count(answer) > 0: 
        return True
    else: 
        return False

def set_pixel_color(num_of_pixel, color="", timeout=0.1):
    """pixel color setting
    color is expected in RRGGBB string format
    """
    if type(num_of_pixel) != int or num_of_pixel not in range(0, 135): 
        return False
    command = "x{} {}\n".format(num_of_pixel, color)
    return send_to_panel(command, command, timeout)

def panel_show():
    """panel refresh
    usually required after panel video memory changing
    """
    command = "show\n"
    return send_to_panel(command)

def panel_clear(): 
    """all pixels switching off"""
    command = "clear\n"
    return send_to_panel(command)

def demo(): 
    """simple demo in arduino"""
    command = "demo\n"
    return send_to_panel(command)

def rainbow(): 
    """rainbow demo in arduino"""
    command = "rainbow\n"
    return send_to_panel(command)

def stop(): 
    """stop demos in arduino"""
    command = "stop\n"
    return send_to_panel(command)

def set_panel_color(color="", timeout=0.1):
    """all pixels setup to one color
    color is expected in RRGGBB string format
    """
    command = "color {}\n".format(color)
    return send_to_panel(command, command, timeout)

def set_panel_memory(rgb_string, from_pixel=0, timeout=0.1):
    """sending data into panel video memory
    rgb_string is in binary format - 3 bytes a pixel
    is necessary to send data in 3 bytes groups (3 bytes for a pixel)
    maximal data block length is 128B - usual size of Arduino input buffer
    long rgb_string is splitted into more memblocks
    !!! after data upload panel is NOT refreshed - panel_show() is required !!!
    """
    data_len = len(rgb_string)
    rgb_string += "\x00" * (data_len % 3) 
    memblock_len = 120
    count_of_pixels = memblock_len / 3
    number_of_memblocks = data_len / memblock_len 
    if data_len % memblock_len: 
        number_of_memblocks += 1
    for memblock in range(number_of_memblocks):
        data = rgb_string[memblock * memblock_len:(memblock + 1) * memblock_len]
        command = "m{} {}\n".format(from_pixel + memblock * count_of_pixels, \
                len(data) / 3)
        result = send_to_panel(command, command, timeout)
        if result: 
            result = send_to_panel(data, "OK\n", timeout)
        else: 
            break
    return result
    
def setup(speed=115200):
  # Start Serial2 at speed baud:
  Serial2.begin(speed)

def read():
    """read and return all data from input serial buffer"""
    data = ""
    while Serial2.available():
        data += Serial2.read()
    return data

def rotate(l,n):
    """ list rotation """
    return l[n:] + l[:n]

def matrix(row, column): 
    """counting of pixel order number
    from row and column
    """
    if row not in range(0, 9) or column not in range(0, 15):
        return False
    if not row % 2:
        # even line
        return row * 15 + column
    else: 
        # odd line
        return (row + 1) * 15 - column - 1

def rectangle(llr, llc, rur, ruc, color="0"): 
    """show rectangle with color 
    using set_pixel_color() and matrix()"""
    row = llr
    col = llc
    row_steps = rur - llr
    col_steps = ruc - llc
    led = matrix(row, col)
    result = set_pixel_color(led, color)
    for increment in [[0, 1], [1, 0], [0, -1], [-1, 0]]: 
        new_row = row + increment[0] * row_steps
        new_col = col + increment[1] * col_steps
        while row != new_row or col != new_col: 
            led = matrix(row, col)
            result = True
            if not (led is False):
                result = set_pixel_color(led, color)
                if not result: 
                    break
            row += increment[0]
            col += increment[1]
    return result

def smile(): 
    """simple test with panel pixels map"""
    rows = 9
    cols = 15
    mapa = [["" for col in range(cols)] for row in range(rows)]
    return mapa

def circle(pixel_map, center_x=7, center_y=4, diameter=4, color="33"):
    for angle_step in range(diameter * 8):
        x = center_x + int(diameter * math.sin(2 * math.pi / diameter / 8 * \
                angle_step))
        y = center_y + int(diameter * math.cos(2 * math.pi / diameter / 8 * \
                angle_step))
        print x, y
        if (x in range(len(pixel_map[0]))) and (y in range(len(pixel_map))): 
            pixel_map[y][x] = color
    return pixel_map

def test5():
    colors = ["aa", "aa00", "aa0000", "aaaa", "aa00aa", "aaaa00", "222222"]
    for size in range(1, 5): 
        for row in range(9 / size + 1): 
            for col in range(15 / size + 1): 
                rectangle(row * size, col * size, row * size + size - 1,\
                        size * (col + 1) - 1, colors[(col + row) % len(colors)])
        time.sleep(2)
        panel_clear()
        time.sleep(1)


def test3(colors=["ff", "ff00", "ff0000","333300", "330033", "3333", "0"]):
    """test with rectangles"""
    row = 4
    col = 7
    for color in colors: 
        for step in range(8):
            result = rectangle(row - step, col - step, row + step, col + step, \
                    color)
            time.sleep(0.2)
    return result

def test4(count=100, colors=["ff", "ff00", "ff0000","333300", "330033", \
        "3333"]):
    """test with rectangles"""
    num_of_colors = len(colors)
    num_of_rect = 5
    for i in range(count): 
        d = i % num_of_rect
        result = rectangle(d, d, 8 - d, 14 - d, \
                colors[i % num_of_colors])
        time.sleep(0.1)
    return result

def test2(colors=["ff", "ff00", "ff0000", "0"]):
    """diagonal lines - using matrix transformation"""
    for color in colors: 
        for c in range(-10, 15):
            for r in range(0, 9):
                led = matrix(r, c + r)
                if not (led is False): 
                    result = set_pixel_color(led, color)
                    if not result: 
                        break
    for color in colors: 
        for c in range(14 + 8, -1, -1):
            for r in range(0, 9):
                led = matrix(r, c - r)
                if not (led is False): 
                    result = set_pixel_color(led, color)
                    if not result: 
                        break
    for color in colors: 
        for c in range(14, -11, -1):
            for r in range(0, 9):
                led = matrix(r, c + r)
                if not (led is False): 
                    result = set_pixel_color(led, color)
                    if not result: 
                        break
    for color in colors: 
        for c in range(0, 23):
            for r in range(0, 9):
                led = matrix(r, c - r)
                if not (led is False): 
                    result = set_pixel_color(led, color)
                    if not result: 
                        break
    return result

def test(count=12):
    """pixel show test"""
    for b in range(1, count + 1):
        for i in range(135):
            command = "x{} {}\n".format(i, hex((b % 4 == 1) * 255 + (b % 4 == \
                    2) * 256 * 255 + (b % 4 == 3) * 256 * 256 * 255)[2:])
            result = send_to_panel(command)
            if not result: 
                break
    return result

def test1(count=1000, start_number=0):
    """test of writing into panel video memory"""
    r = 0.5
    g = 0
    b = 0
    data_pattern = '\x00\x00\x00\x10\x10\x10   @@@'
    count_of_pixels = 40
    begin_time = time.time()
    for change_number in range(start_number, start_number + count):
        for memblock in range(4):
            # apply rgb modifying
            r = max(math.sin(change_number/50.), 0)
            g = max(math.sin(change_number/50. + math.pi * 2 / 3), 0)
            b = max(math.sin(change_number/50. + math.pi * 4 / 3), 0)
            modif_data_pattern = ""
            for i in range(len(data_pattern)):
                modif_data_pattern += chr(int(ord(data_pattern[i]) * \
                    (r * (i % 3 == 0) + g * (i % 3 == 1) + b * (i % 3 == 2))))
            data = rotate(modif_data_pattern, (change_number * 3) % \
                    len(data_pattern)) * (count_of_pixels * 3 / \
                    len(data_pattern))
            # data writing
            command = "m{} {}\n".format(memblock * count_of_pixels, \
                    count_of_pixels)
            result = send_to_panel(command)
            if result: 
                result = send_to_panel(data, "OK\n")
            else: 
                break
        if result: 
            result = panel_show() 
    end_time = time.time()
    if result: 
        print "{} changes".format(count)
        print "total time {} seconds".format(end_time - begin_time)
        print "one change period {} seconds".format((end_time - begin_time) \
                / count)
    return result

def oldtest1(count=1000):
    """test of writing into panel video memory"""
    r = 0.5
    g = 0
    b = 0
    data_pattern = '\x00\x00\x00\x10\x10\x10   @@@'
    count_of_pixels = 40
    begin_time = time.time()
    for change_number in range(count):
        for memblock in range(4):
            command = "m{} {}".format(memblock * count_of_pixels, \
                    count_of_pixels)
            Serial2.write(command + "\n")
            itime = time.time()
            icommand = ""
            while(icommand.count(command)==0 and time.time() < itime + 0.1):
                icommand += Serial2.read()
            # apply rgb modifying
            r = max(math.sin(change_number/50.), 0)
            g = max(math.sin(change_number/50. + math.pi * 2 / 3), 0)
            b = max(math.sin(change_number/50. + math.pi * 4 / 3), 0)
            modif_data_pattern = ""
            for i in range(len(data_pattern)):
                modif_data_pattern += chr(int(ord(data_pattern[i]) * \
                    (r * (i % 3 == 0) + g * (i % 3 == 1) + b * (i % 3 == 2))))
            # data writing
            data = rotate(modif_data_pattern, (change_number * 3) % \
                    len(data_pattern)) * (count_of_pixels * 3 / \
                    len(data_pattern))
            Serial2.write(data)
            itime = time.time()
            icommand = ""
            while(icommand.count("OK")==0 and icommand.count("KO")==0 and \
                    time.time() < itime + 0.1):
                icommand += Serial2.read()
        command = "show"
        Serial2.write(command + "\n")
        itime = time.time()
        icommand = ""
        while(icommand.count(command)==0 and time.time() < itime + 0.1):
            icommand += Serial2.read()
        #print icommand
 
    end_time = time.time()
    print "{} changes".format(count)
    print "total time {} seconds".format(end_time - begin_time)
    print "one change period {} seconds".format((end_time - begin_time) / count)
    return #ser

def winit(address=None, num_of_tries=3):
    """init with address obtaining with hcitool scan
    is quicker and enables more wiimotes!!! 

    my current wiimotes: 
    white: 00:24:1E:A7:C4:90
    black: 00:26:59:F6:A0:75 (Honza Vancl)
    """
    print "na wii ovladaci zmacknout tlacitka 1 a 2 !!!"
    print "press 1 and 2 button on a wiimote!!!"
    wm = None
    ok = False
    iinit = 0
    while not ok and iinit < num_of_tries:
        # print iinit  
        try: 
            if address is None: 
                wm = cwiid.Wiimote()
            else: 
                wm = cwiid.Wiimote(address)
            wm.rumble = 1 
            time.sleep(0.2)
            wm.rumble = 0
            wm.rpt_mode = cwiid.RPT_IR | cwiid.RPT_BTN
            ok = True 
        except: 
            ok = False
            iinit += 1
    ok = False
    return wm

def test_wii():
    """simple test of wiimote communication"""
    w = winit()
    print "konec inicializace"
    print "end of initialisation"
    time.sleep(1)
    try:
        """ 
        w.rumble = 1 
        time.sleep(0.2)
        w.rumble = 0
        """
        """4 leds on the wiimote show numbers in binary form"""
        for i in range(16): 
            w.led = i
            time.sleep(0.5)
        time.sleep(1)
        w.led = 0
    except: 
        print "nebyla navazana komunikace s ovladacem..."
    return w

def test_wii_buttons(wi): 
    """pixel moving with wiimote buttons 
    wi - wimote instance
    """
    bckg_color = ""
    color = "44"
    position = [0, 0]
    old_position = [-1, -1]
    play = True
    while play: 
        if position != old_position: 
            set_pixel_color(matrix(old_position[0], old_position[1]), \
                    bckg_color)
            set_pixel_color(matrix(position[0], position[1]), color)
            old_position = position[:]
            time.sleep(0.1)
        buttons = wi.state["buttons"]
        if buttons & 4:
            # trigger
            fire(position)
            old_position = [-1000, -1000]
        if buttons & 256:
            # left
            position[1] -= 1
        if buttons & 512:
            # right
            position[1] += 1
        if buttons & 2048:
            # up
            position[0] += 1
        if buttons & 1024:
            # down
            position[0] -= 1
        if buttons & 8:
            # A button
            # go to left bottom
            position[0] = 0
            position[1] = 0
        if buttons & 128:
            # Home button
            play = False

def fire(position):
    """fire - red fadeout at the position"""
    for reds in [255, 128, 64, 32, 16, 8, 4, 2, 0]: 
        set_pixel_color(matrix(position[0], position[1]), hex(reds)[2:] + \
                "0000")
        time.sleep(0.05)


class Snake(object): 
    """snake game class
    my own version of snake game
    """
    """
    snake pixels
    each pixel is a list of [row, column, color]
    pixel[0] is the head pixel
    color in "RRGGBB" string form
    """
    pixels = [] 
    max_row = 8
    max_col = 14
    default_colors = ["ff", "44"]
    blank_color = ""
    position = [0, 0]
    food =  {
            "position": [0, 0], 
            "color": "666600", 
            "start_time": 0,
            "duration": 0, 
            "df_duration": [3, 8], 
            "df_interval": [0, 0], 
            "active": False, 
            "visible": False
            }
    out_enable = True
    def food_service(self): 
        """food controlling"""
        f = self.food
        if f["active"] and not f["visible"] and f["start_time"] < time.time():
            # show food at a free pixel
            # free position finding
            # random position
            r = random.randint(0, self.max_row)
            c = random.randint(0, self.max_col)
            # first free position next to random position
            num_of_cells = (self.max_row + 1) * (self.max_col + 1)
            while [r, c] in [coord[:2] for coord in self.pixels] and \
                    num_of_cells:
                c += 1
                if c > self.max_col: 
                    c = 0
                    r += 1
                    if r > self.max_row: 
                        r = 0
                num_of_cells -= 1
            if num_of_cells: 
                # free position found
                # show food at [r, c]
                set_pixel_color(matrix(r, c), f["color"])
                f["position"] = [r, c]
                f["visible"] = True
        elif f["active"] and f["visible"] and (f["start_time"] + \
                f["duration"]) > time.time():
            # a food is in progress
            # test if snake reached the food
            if self.food["position"] in [coord[:2] for coord in \
                    self.pixels]:
                self.add_pixel()
                f["active"] = False
                f["visible"] = False
            return
        elif f["active"] and not f["visible"] and f["start_time"] > time.time():
            # wait to show
            return
        else: 
            # old food hiding
            if f["visible"]:
                pos = f["position"]
                set_pixel_color(matrix(pos[0], pos[1]), self.blank_color)
                f["visible"] = False
            # new food generation
            t1 = f["df_interval"][0] * 1000
            t2 = f["df_interval"][1] * 1000
            d1 = f["df_duration"][0] * 1000
            d2 = f["df_duration"][1] * 1000
            f["start_time"] = time.time() + random.randint(t1, t2) / 1000.
            f["duration"] = random.randint(d1, d2) / 1000.
            f["active"] = True
            f["visible"] = False
    def add_pixel(self, row=None, col=None, color=None):
        """add pixel at the end of snake"""
        if type(row) != int and len(self.pixels) == 0: 
            row = self.position[0]
        if type(col) != int and len(self.pixels) == 0: 
            col = self.position[1]
        if color is None: 
            color = self.default_colors[min(len(self.pixels), \
                    len(self.default_colors) - 1)]
        self.pixels.append([row, col, color])
    def del_pixel(self): 
        """delete the last pixel of the snake"""
        if len(self.pixels) > 0: 
            last_pixel = self.pixels[-1][:]
            set_pixel_color(matrix(last_pixel[0], last_pixel[1]), \
                    self.blank_color)
            self.pixels.remove(self.pixels[-1])
    def show(self): 
        """show the snake on the light panel"""
        for pixel in self.pixels: 
            set_pixel_color(matrix(pixel[0], pixel[1]), pixel[2])
    def move(self):
        """snake moving"""
        if len(self.pixels) > 0: 
            last_pixel = self.pixels[-1][:]
            for index in range(len(self.pixels)-1, 0, -1):
                self.pixels[index][0] = self.pixels[index - 1][0]
                self.pixels[index][1] = self.pixels[index - 1][1]
            self.pixels[0][0] = self.position[0]
            self.pixels[0][1] = self.position[1]
            # last pixel hiding
            set_pixel_color(matrix(last_pixel[0], last_pixel[1]), \
                    self.blank_color)
            # snake show (the whole snake or first two pixels
            # it depends on number of colors in the snake
            for pixel in self.pixels[:2]: 
                set_pixel_color(matrix(pixel[0], pixel[1]), pixel[2])
    def wii_move(self, wi=None):
        """the snake controlling through wiimote
        wi is wiimote object returned from winit()
        """
        if wi is None: 
            """ wiimote initializing """
            wi = winit()
        old_position = [-1, -1]
        play = True
        while play:
            move_flag = False
            if len(self.pixels) > 0: 
                self.position = [self.pixels[0][0], self.pixels[0][1]][:]
            if self.position != old_position: 
                old_position = self.position[:]
                time.sleep(0.1)
            buttons = wi.state["buttons"]
            if buttons & 4:
                # trigger
                fire(self.position)
                old_position = [-1000, -1000]
                if len(self.pixels) > 0: 
                    fp = self.pixels[0]
                    set_pixel_color(matrix(fp[0], fp[1]), fp[2])
            if buttons & 256:
                # left
                if self.out_enable or self.position[1] > 0: 
                    self.position[1] -= 1
                    move_flag = True
            if buttons & 512:
                # right
                if self.out_enable or self.position[1] < self.max_col: 
                    self.position[1] += 1
                    move_flag = True
            if buttons & 2048:
                # up
                if self.out_enable or self.position[0] < self.max_row: 
                    self.position[0] += 1
                    move_flag = True
            if buttons & 1024:
                # down
                if self.out_enable or self.position[0] > 0: 
                    self.position[0] -= 1
                    move_flag = True
            if buttons & 8:
                # A button
                # go to left bottom
                """
                the snake head goes to the [0, 0] position
                the rest of the snake leaves at the current position
                """
                # the old snake head hiding
                set_pixel_color(matrix(self.pixels[0][0], self.pixels[0][1]), \
                        self.blank_color)
                self.position[0] = 0
                self.position[1] = 0
                self.pixels[0][0] = self.pixels[0][1] = 0
                # show the new head (see moving)
                for pixel in self.pixels[:2]: 
                    set_pixel_color(matrix(pixel[0], pixel[1]), pixel[2])
            if buttons & 128:
                # Home button
                # end of controlling loop
                play = False
            if buttons & cwiid.BTN_PLUS:
                """add pixel to snake"""
                self.add_pixel()
                old_position = [-1000, -1000]
                fp = self.pixels[0]
                set_pixel_color(matrix(fp[0], fp[1]), fp[2])
                # wait for button release
                while wi.state["buttons"] & cwiid.BTN_PLUS:
                    pass
            if buttons & cwiid.BTN_MINUS:
                """delete pixel at the end of the snake"""
                self.del_pixel()
                old_position = [-1000, -1000]
                # wait for button release
                while wi.state["buttons"] & cwiid.BTN_MINUS:
                    pass
            if buttons & cwiid.BTN_1:
                """out_enable toggle"""
                self.out_enable = not self.out_enable
                # wait for button release
                while wi.state["buttons"] & cwiid.BTN_1:
                    pass
            if move_flag: 
                self.move()
            """testing if the snake doesn't have the head on his own body"""
            if len(self.pixels) > 1 and [self.pixels[0][0], self.pixels[0][1]] \
                    in [coord[:2] for coord in self.pixels[1:]]:
                # colision - end of game
                for blink in range(3): 
                    set_panel_color("ff0000")
                    time.sleep(0.1)
                    set_panel_color("")
                    time.sleep(0.1)
                self.pixels = []
                self.position = [0, 0]
                self.add_pixel()
                fire(self.position)
                fp = self.pixels[0]
                set_pixel_color(matrix(fp[0], fp[1]), fp[2])
            # food controlling
            self.food_service()
                

