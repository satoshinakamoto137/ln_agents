# ============================================
# 🐉 Himeryu Event Generator Engine
# ============================================
import random
import time
from datetime import datetime
import linked_scripts as linked_horizon

# === Delay Models ===
def gaussian_delay(mean=0.08, stddev=0.02, max_time=0.3):
    delay = min(max(0, random.gauss(mean, stddev)), max_time)
    time.sleep(delay)
    return delay

def lognormal_delay(mu=0.05, sigma=0.04, max_time=0.4):
    delay = min(random.lognormvariate(mu, sigma), max_time)
    time.sleep(delay)
    return delay

# === Event Generator ===
def himeryu_event_generator(mu=2.71, sigma=0.33, total_events=10):
    """
    Generador real de eventos.
    Cada evento espera un tiempo (en minutos, distribuido log-normalmente)
    y luego ejecuta una acción: imprimir un mensaje.
    """
    print(f"🚀 Starting Himeryu Event Generator at {datetime.now()}")
    print(f"📈 Using log-normal distribution (μ={mu}, σ={sigma}) for delay (minutes)\n")

    for i in range(1, total_events + 1):
        # Calcular tiempo hasta el siguiente evento (en minutos)
        event_minutes = round(random.lognormvariate(mu, sigma), 2)
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] ⏳ Event {i:03d} → executing in {event_minutes} minutes")

        # Esperar el tiempo real del evento
        delay_seconds = event_minutes * 60
        time.sleep(delay_seconds)

        # Acción del evento
        now = datetime.now().strftime("%H:%M:%S")
        print(f"[{now}] 💖 Hola, event by Mei🥰 (Event {i:03d}) executed!\n")
        linked_horizon.script_add_contact(added_conntacts=2, recording=True, return2center=True)

        # Pequeña variación de microtiempo entre eventos
        lognormal_delay(mu=0.05, sigma=0.04, max_time=0.4)

    print("✅ All events executed successfully.")

# === Run Example ===
if __name__ == "__main__":
    # Esto generará 5 eventos que ocurren a intervalos lognormales (10–20 min aprox)
    himeryu_event_generator(mu=2.71, sigma=0.33, total_events=7)
