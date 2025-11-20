import serial
import time
import pyautogui
import time, random, serial
import linked_scripts as ls

ARDUINO_PORT = ls.ARDUINO_PORT
BAUD_RATE = 9600

def send_command_bk1(ser, cmd):
    ser.write((cmd + '\n').encode())
    time.sleep(0.005)  # Tiny delay to not overwhelm the serial buffer

def send_command(ser, cmd):
    ser.write((cmd + '\n').encode())

    # 💡 Wait for Arduino to reply "OK"
    while True:
        line = ser.readline().decode().strip()
        if line == "OK":
            break

def move_x(ser, steps):
    direction = "MOVE X" if steps > 0 else "MOVE -X"
    for _ in range(abs(steps)):
        send_command(ser, direction)

def move_y(ser, steps):
    direction = "MOVE Y" if steps > 0 else "MOVE -Y"
    for _ in range(abs(steps)):
        send_command(ser, direction)


def calibrate_linear(): #this function works ok, but when the moves on y are to long it take so much time to finish, is "stuck" on the left side
    try:
        print("🔌 Connecting to Arduino...")

        with serial.Serial(ARDUINO_PORT, BAUD_RATE, timeout=2) as arduino:
            time.sleep(3)  # Wait for Arduino boot
            
            print("📐 Calibrating to screen bottom-left...")

            # Move left as far as we can
            for _ in range(500):
                send_command(arduino, "MOVE -X")

            # Move down as far as we can
            for _ in range(500):                   #if it dont strike left, can move down
                send_command(arduino, "MOVE Y")

            send_command(arduino, "CLICK")
            print("✅ Calibrated!")

    except Exception as e:
        print(f"❌ Error: {e}")


def generate_trajectory(start, end, deviation=10, speed=3):
    """
    Generates a smooth bezier trajectory from start to end point.
    Returns a list of (x, y) points.
    """
    from random import choice, randint
    from math import ceil

    def pascal_row(n):
        result = [1]
        x, numerator = 1, n
        for denominator in range(1, n//2+1):
            x *= numerator
            x /= denominator
            result.append(x)
            numerator -= 1
        if n & 1 == 0:
            result.extend(reversed(result[:-1]))
        else:
            result.extend(reversed(result))
        return result

    def make_bezier(xys):
        n = len(xys)
        combinations = pascal_row(n - 1)
        def bezier(ts):
            result = []
            for t in ts:
                tpowers = (t**i for i in range(n))
                upowers = reversed([(1-t)**i for i in range(n)])
                coefs = [c*a*b for c, a, b in zip(combinations, tpowers, upowers)]
                result.append(list(sum([coef*p for coef, p in zip(coefs, ps)]) for ps in zip(*xys)))
            return result
        return bezier

    ts = [t / (speed * 100.0) for t in range(speed * 101)]

    dx = abs(ceil(end[0]) - ceil(start[0]))
    dy = abs(ceil(end[1]) - ceil(start[1]))

    control_1 = (
        start[0] + choice((-1, 1)) * dx * 0.01 * randint(deviation // 2, deviation),
        start[1] + choice((-1, 1)) * dy * 0.01 * randint(deviation // 2, deviation),
    )
    control_2 = (
        start[0] + choice((-1, 1)) * dx * 0.01 * randint(deviation // 2, deviation),
        start[1] + choice((-1, 1)) * dy * 0.01 * randint(deviation // 2, deviation),
    )

    xys = [start, control_1, control_2, end]
    bez = make_bezier(xys)
    points = bez(ts)

    return [(round(x), round(y)) for x, y in points]

def run_trajectory(trajectory, ser):
    """
    Receives a list of (x, y) absolute trajectory points.
    Calculates deltas between steps and sends low-level MOVE commands.
    """
    if not trajectory or len(trajectory) < 2:
        print("❗ Not enough points.")
        return

    prev_x, prev_y = trajectory[0]

    for x, y in trajectory[1:]:
        dx = x - prev_x
        dy = y - prev_y

        move_x(ser, dx)
        move_y(ser, dy)

        prev_x, prev_y = x, y

def test_movs_bk1():
    try:
        print("🔌 Connecting to Arduino...")
        with serial.Serial(ARDUINO_PORT, BAUD_RATE, timeout=2) as arduino:
            time.sleep(3)  # Wait for Arduino boot
            
            print("📐 Calibrating to screen bottom-left...")

            # Move left as far as we can
            for _ in range(1000):
                send_command(arduino, "MOVE -X")

            print("Waiting 5 seconds...")
            time.sleep(5)

            # Move down as far as we can
            for _ in range(1000):
                send_command(arduino, "MOVE Y")

            #send_command(arduino, "CLICK")
            print("✅ Moved!")

    except Exception as e:
        print(f"❌ Error: {e}")

def simple_calibrate():
    try:
        print("🔌 Connecting to Arduino...")
        with serial.Serial(ARDUINO_PORT, BAUD_RATE, timeout=2) as arduino:
            time.sleep(3)  # Wait for Arduino to reset

            print("📐 Calibrating to screen bottom-left...")
            move_x(arduino, -1000)  # Move left
            #time.sleep(5)
            move_y(arduino, 1000)   # Move down
            print("✅ Moved to bottom-left corner!")

    except Exception as e:
        print(f"❌ Error: {e}")

def get_cursor_position():
    """
    Returns the current position of the mouse cursor.
    Non-intrusive — no movement, no clicks.
    Just quiet observation. 🌸
    """
    x, y = pyautogui.position()
    return (x, y)

def get_screen_size():
    width, height = pyautogui.size()
    return width, height

def human_like_calibrate():
    """
    Uses a smooth human-like Bézier trajectory to move to bottom-left corner.
    Simulates natural movement instead of robotic edge bumping.
    """
    try:
        print("🔌 Connecting to Arduino for human-like calibration...")

        with serial.Serial(ARDUINO_PORT, BAUD_RATE, timeout=2) as arduino:
            time.sleep(3)

            print("✨ Generating human-like path to bottom-left...")

            # Virtual starting point is (0, 0)
            # Target is far left and down
            target_x = -1000
            target_y = 1000
            path = generate_trajectory((0, 0), (target_x, target_y), deviation=12, speed=4)

            print("📍 Sending human-like calibration path...")
            run_trajectory(path, arduino)

            print("✅ Calibrated to bottom-left with elegance~")

    except Exception as e:
        print(f"❌ Error: {e}")

def gaussian_delay(mean=0.08, stddev=0.02, max_time=0.3):
    delay = min(max(0, random.gauss(mean, stddev)), max_time)
    time.sleep(delay)
    return delay

def lognormal_delay(mu=0.05, sigma=0.04, max_time=0.4):
    delay = min(random.lognormvariate(mu, sigma), max_time)
    time.sleep(delay)
    return delay

def random_step_count(model='gaussian', max_steps=5, min_steps=2, mean=3.2, stddev=1.1, mu=1, sigma=0.6):
    if model == 'gaussian':
        steps = int(random.gauss(mean, stddev))
    else:
        steps = int(random.lognormvariate(mu, sigma))
    return max(min_steps, min(max_steps, steps))

def click_advanced_delay(
    side='left',
    delay_model='gaussian',
    max_time=5,      # Max allowed delay (seconds) before the click happens
    arduino_port=None,
    baud_rate=9600
):
    """
    side: 'left', 'right', or 'middle'
    delay_model: 'gaussian' or 'lognormal'
    max_time: maximum wait time before clicking (in seconds)
    arduino_port: your Arduino port (e.g. '/dev/ttyACM0')
    baud_rate: Serial baudrate
    """

    if not arduino_port:
        print("❌ Arduino port not specified!")
        return

    # 1. Delay before click (simulate real user hesitation)
    if delay_model == 'gaussian':
        t = gaussian_delay(mean=0.07, stddev=0.04, max_time=max_time)
        print(f"🕰️ Gaussian delay: {round(t, 3)}s before click")
    else:
        t = lognormal_delay(mu=0.05, sigma=0.04, max_time=max_time)
        print(f"🕰️ Lognormal delay: {round(t, 3)}s before click")

    # 2. Decide click type
    if side == 'left':
        cmd = "CLICK"
    elif side == 'right':
        cmd = "RIGHT_CLICK"  # Make sure Arduino knows this
    elif side == 'middle':
        cmd = "MIDDLE_CLICK" # Make sure Arduino knows this
    else:
        print("❌ Unknown side argument")
        return

    # 3. Send command to Arduino
    try:
        with serial.Serial(arduino_port, baud_rate, timeout=2) as arduino:
            arduino.write((cmd + '\n').encode())
            print(f"🖱️ Sent {side}-click command to Arduino ({arduino_port})")

            # Wait for optional Arduino ACK if you want:
            ack = arduino.readline().decode().strip()
            print(f"🔔 Arduino says: {ack}")

    except Exception as e:
        print(f"❌ Serial error during click: {e}")


def go_to_position(
    target_x, target_y,
    steps=None, tolerance=2,
    time_limit=5,
    smart_pixel=True,
    final_step=True,
    delay_model='gaussian',
    step_count_model='gaussian',
    small_mistake_prob=5,
    noise_timing='gaussian',
    hesitation_prob=5
):
    print("🔥 Entrando a go_to_position()")
    start_time = time.time()
    if steps is None:
        steps = random_step_count(model=step_count_model)
    print(f"🔢 Steps chosen: {steps}")

    for i in range(steps):
        elapsed = time.time() - start_time
        if elapsed > time_limit:
            print("⏰ Time limit reached during trajectory!")
            break

        current_x, current_y = get_cursor_position()
        print(f"⭐ Paso {i+1} - Current pos: {current_x}, {current_y}")
        dx = target_x - current_x
        dy = target_y - current_y
        print(f"📐 Calculando delta: dx={dx}, dy={dy}")

        frac = 1.0 / (steps - i)
        move_dx = int(dx * frac)
        move_dy = int(dy * frac)

        if random.randint(1, 100) <= small_mistake_prob:
            oops_x = random.choice([-1, 1]) * random.randint(10, 30)
            oops_y = random.choice([-1, 1]) * random.randint(10, 30)
            print(f"😳 Oops! Mistake: Δx={oops_x}, Δy={oops_y}")
            move_dx += oops_x
            move_dy += oops_y

        base_dev = max(6, int(abs(move_dx + move_dy) / 60))
        base_speed = max(2, min(6, int(abs(move_dx + move_dy) / 100)))

        print(f"🚶 Move #{i+1}: Δx={move_dx}, Δy={move_dy}, dev={base_dev}, speed={base_speed}")
        points = generate_trajectory((0, 0), (move_dx, move_dy), deviation=base_dev, speed=base_speed)
        print(f"🖌️ Trajectory points: {points[:5]}... ({len(points)} points)")

        try:
            with serial.Serial(ARDUINO_PORT, BAUD_RATE, timeout=2) as arduino:
                print("🔌 Serial abierto, enviando trayectoria...")
                run_trajectory(points, arduino)
        except Exception as e:
            print(f"❌ Error serial: {e}")

        if noise_timing == 'gaussian':
            gaussian_delay()
        else:
            lognormal_delay()

        if random.randint(1, 100) <= hesitation_prob:
            pause_duration = round(random.uniform(0.4, 1.0), 2)
            print(f"😶‍🌫️ Hesitation pause: {pause_duration}s")
            time.sleep(pause_duration)

        new_x, new_y = get_cursor_position()
        print(f"🍑 Nuevo pos: {new_x}, {new_y}")
        if abs(target_x - new_x) <= tolerance and abs(target_y - new_y) <= tolerance:
            print(f"💘 Reached within tolerance: ({new_x}, {new_y})")
            return

    if smart_pixel:
        print("🛠️ Final pixel correction...")
        current_x, current_y = get_cursor_position()
        dx = target_x - current_x
        dy = target_y - current_y
        try:
            with serial.Serial(ARDUINO_PORT, BAUD_RATE, timeout=2) as arduino:
                move_x(arduino, dx)
                move_y(arduino, dy)
                if final_step:
                    for _ in range(random.randint(1, 2)):
                        move_x(arduino, random.choice([-1, 1]))
                        move_y(arduino, random.choice([-1, 1]))
                        gaussian_delay()
        except Exception as e:
            print(f"❌ Error serial (final correction): {e}")

    final_x, final_y = get_cursor_position()
    print(f"✅ Final position: ({final_x}, {final_y})")


def mouse_scrolling(steps: int, port=None, baudrate=9600):
    """
    Envía comandos de scroll al dispositivo Arduino.

    steps > 0  ⇒ scroll arriba
    steps < 0  ⇒ scroll abajo
    """
    try:
        with serial.Serial(port, baudrate, timeout=1) as ser:
            time.sleep(2)  # espera a que se inicialice

            direction = "SCROLL UP" if steps > 0 else "SCROLL DOWN"
            for _ in range(abs(steps)):
                ser.write((direction + "\n").encode())
                time.sleep(0.05)  # pequeño delay entre comandos
            print("Scroll enviado:", direction, "x", abs(steps))

    except serial.SerialException as e:
        print("💔 Error al conectar con el dispositivo:", e)


'''
if __name__ == "__main__":
    #simple_calibrate()
    #human_like_calibrate()

    #time.sleep(5)

    #points = generate_trajectory((0, 0), (100, -100), deviation=15, speed=4)

    #print("💠 Generated trajectory:")
    #for pt in points:
        #print(pt)

    #print("🧭 Sending trajectory to Arduino...")

    #with serial.Serial(ARDUINO_PORT, BAUD_RATE, timeout=2) as arduino:
        #time.sleep(3)
        #run_trajectory(points, arduino)

    #print("✅ Trajectory complete!")

    x_pos, y_pos = get_cursor_position()
    print(f"🖱️ Current cursor position: {x_pos}, {y_pos}")

    #w, h = get_screen_size()
    #print(f"🖥️ Your screen resolution is: {w} x {h}")

    #go_to_position(720, 450)
    #go_to_position(720, 450, steps=3, tolerance=1, smart_pixel=True, final_step=True, time_limit=5)
    
    go_to_position(
    720, 450,
    steps=None,            # Let it choose with gaussian by default
    tolerance=2,
    time_limit=5,
    smart_pixel=True,
    final_step=True,
    delay_model='gaussian',
    step_count_model='gaussian',  # 'lognormal' if you want more variance
    small_mistake_prob=5,         # 5% chance to "miss" like a human
    noise_timing='gaussian',
    hesitation_prob=5  )           # 5% chance to "pause and think" 
    
    x_pos, y_pos = get_cursor_position()
    print(f"🖱️ Current cursor position: {x_pos}, {y_pos}")

'''

#click_advanced_delay(side='right', delay_model='gaussian', max_time=4, arduino_port='/dev/ttyACM0')
