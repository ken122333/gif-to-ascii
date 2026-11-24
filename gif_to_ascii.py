from PIL import Image, ImageSequence 
import sys 
import shutil
import time 

brightness_ramps = { 
    "1": " .:-=+*#%@",  
    "2": " .+#@",  
    "3": " .'`^\",:;Il!i~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$",  
    "4": " \u2591\u2592\u2593\u2588",
}

brightness_characters = brightness_ramps["3"]
ascii_frames = []  
grayscale = False  
path = "gif3.gif" 

def frame_to_ascii(frame, width, height):  # convert one gif frame to terminal text
    rgba = frame.convert("RGBA") 
    background = Image.new("RGB", rgba.size, "black") # create new image in the same size with a black background
    background.paste(rgba, mask=rgba.getchannel("A")) # put frame onto black background so transparent will be seen as black
    resized = background.resize((width, height), Image.Resampling.LANCZOS)  # resize the image to one pixel per character cell. lanczos resamping to interpolate color at each point

    colors = list(resized.getdata())  # list of colors of each pixel
    brightness_values = list(resized.convert("L").getdata())  # converts image into grayscale and creates a list of brightness values at each point

    cells = [] 
    for (red, green, blue), brightness in zip(colors, brightness_values):  # loop through each pixel with its brightness and color
        index = brightness * (len(brightness_characters) - 1) // 255  # assign brightness to a brightness character index
        if grayscale:
            cells.append(f"\x1b[38;2;{brightness};{brightness};{brightness}m{brightness_characters[index]}")  
        else: 
            cells.append(f"\x1b[38;2;{red};{green};{blue}m{brightness_characters[index]}")  # assign character and text color
    rows = []
    for start in range(0, len(cells), width): #join cells for each row into a string
        row = "".join(cells[start:start + width])
        rows.append(row)

    return "\x1b[0m\n".join(rows) + "\x1b[0m"

def gif_to_ascii(gif_path, columns, rows): 
    frames = [] 
    with Image.open(gif_path) as gif: 
        max_width = max(1, columns)  
        max_height = max(1, rows - 1)  
        height_per_column = gif.height / gif.width * 0.5  # 2 columns per row
        width = max(1, min(max_width, int(max_height / height_per_column)))  
        height = max(1, min(max_height, round(width * height_per_column)))

        for frame in ImageSequence.Iterator(gif):  # loop through each gif frame
            delay = (frame.info.get("duration") or 100) / 1000  # converts frame duration into seconds, if the frame duration is missing or 0 it will be set to 100ms
            art = frame_to_ascii(frame, width, height)  # convert gif frame into ascii frame
            frames.append([art,delay])  # store ascii frame and frame duration.
    return frames 
        
try: 
    print("\x1b[?25l", end="", flush=True) #hide cursor
    old_columns, old_rows = 0,0 
    while True:
        columns, rows = shutil.get_terminal_size(fallback=(80, 24))  # get terminal size
        if columns != old_columns or rows != old_rows:  #redraw if terminal is resized
            sys.stdout.write("\x1b[2J")  # clear screen.
            old_columns, old_rows = columns, rows
            ascii_frames = gif_to_ascii(path, columns, rows)
        for frame in ascii_frames:  # loop through all ascii frames
            sys.stdout.write("\x1b[H" + frame[0]) #draw from left top corner
            sys.stdout.flush()  # send frame to terminal
            time.sleep(frame[1])  # wait for frame duration
except KeyboardInterrupt: 
    pass  
finally: 
    print("\x1b[?25h", flush=True) 