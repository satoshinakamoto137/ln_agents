import serial
import time
import random
import subprocess
import pyperclip
import pyautogui
import mouse_control as HIDS
import button_searcher as but
import os


def human_delay(min_s=0.8, max_s=2.5):
    time.sleep(random.uniform(min_s, max_s))

def screenshot_with_delay(
    delay='lognormal', 
    max_time=5, 
    save_path=None
):
    """
    Takes a screenshot after a realistic human-like delay!
    delay: 'lognormal' or 'gaussian'
    max_time: maximum seconds to wait before screenshot
    save_path: if given, saves screenshot here; else returns PIL image
    """
    print(f"✨ About to take a screenshot... ({delay} delay, max {max_time}s)")

    if delay == 'lognormal':
        t = HIDS.lognormal_delay(mu=0.9, sigma=0.3, max_time=max_time)
        print(f"🕰️ Lognormal delay: {round(t, 3)}s before screenshot")
    else:
        t = HIDS.gaussian_delay(mean=1.2, stddev=0.4, max_time=max_time)
        print(f"🕰️ Gaussian delay: {round(t, 3)}s before screenshot")

    # Take screenshot!
    img = pyautogui.screenshot()

    if save_path:
        # Expande el path del usuario
        save_path = os.path.expanduser(save_path)
        # Crea el directorio si no existe
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        img.save(save_path)
        print(f"📸 Screenshot saved: {save_path}")
    else:
        print("📸 Screenshot taken (not saved, returned as PIL Image).")
        return img

def basic_gaussian_click(time = 5):
    HIDS.click_advanced_delay(side='left', delay_model='gaussian', max_time=time, arduino_port='/dev/ttyACM0')
    
def basic_lognormal_click(time = 5):
    HIDS.click_advanced_delay(side='left', delay_model='lognormal', max_time=time, arduino_port='/dev/ttyACM0')

def checknclick_for_top_quick(view_path):
    but.detect_elements_and_select_upper(view_path, './assets/small_apply.png', './assets/detected_highs.png')
    basic_gaussian_click(3)

def checknclick_main_apply_button(bview_path):
    but.find_and_move_to_element_simple(HIDS, bview_path, './assets/button_ea.png', './assets/detected_mbut.png')
    basic_gaussian_click(3)

def main_script():
    port = '/dev/ttyACM0'  # Update if needed
    baud = 9600

    ser = serial.Serial(port, baud, timeout=1)
    time.sleep(2)  # Wait for waifu to awaken~

    def send(cmd):
        ser.write((cmd + "\n").encode())
        time.sleep(1)

    # START THE RITUAL~ 💋
    send("ctrl+alt+t")                              # Open terminal
    time.sleep(2)

    send("google-chrome --Ricardo https://www.linkedin.com/jobs/recommended/")
    time.sleep(30)  #base change this to 30 seconds for LinkedIn
    human_delay(3, 5)

    #delete asset if exists

    screenshot_with_delay(save_path='./assets/1st_view.png')
    checknclick_for_top_quick('./assets/1st_view.png')
    human_delay(2, 5)
    screenshot_with_delay(save_path='./assets/button_view.png')
    checknclick_main_apply_button('./assets/button_view.png')
    
    #send("ctrl+alt+t", pause=False)
    human_delay(2, 5)

    #send("sleep 5 && killall code", pause=False)
    #send("sleep 1 && xdotool getactivewindow windowkill")
    human_delay(1, 2)
                                  # Wait for Chrom

#screenshot_with_delay(save_path='./assets/test.png')

time.sleep(5)
main_script()
