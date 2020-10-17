import subprocess
import time

from gpiozero import OutputDevice


ON_THRESHOLD_CELSIUS = 65   # Temperature at which to start the fan
OFF_THRESHOLD_CELSIUS = 55  # Temperature at which to stop the fan
SLEEP_TIME_SECONDS = 5      # Poll time between subsequent CPU temperature checks
GPIO_FAN = 17               # GPIO pin of the fan


class Fan:

    def __init__(self, gpio_pin):
        self.device = OutputDevice(gpio_pin)

    def is_on(self):
        return bool(self.device.value)

    def is_off(self):
        return not self.is_on()

    def turn_on(self):
        self.device.on()

    def turn_off(self):
        self.device.off()


def main():
    """
    Polls CPU temperature indefinitely.
    Turns fan on if temperature passes upper threshold.
    Turns fan off if temperature passes lower threshold.
    """
    if OFF_THRESHOLD_CELSIUS >= ON_THRESHOLD_CELSIUS:
        raise RuntimeError('OFF_THRESHOLD_CELSIUS must be less than ON_THRESHOLD_CELSIUS')

    fan = Fan(GPIO_FAN)

    while True:
        temperature = get_temperature()

        if temperature >= ON_THRESHOLD_CELSIUS:
            if fan.is_off():
                fan.turn_on()

        elif temperature <= OFF_THRESHOLD_CELSIUS:
            if fan.is_on():
                fan.turn_off()

        time.sleep(SLEEP_TIME_SECONDS)


def get_temperature():
    """
    Get the CPU temperature in degrees Celsius by running vcgencmd as a subprocess.
    Raises:
        RuntimeError: if vcgencmd response cannot be parsed.
    Returns:
        float: The CPU temperature in degrees Celsius.
    """
    output = subprocess.run(['vcgencmd', 'measure_temp'], capture_output=True).stdout.decode()
    try:
        return float(output.split('=')[1].split('\'')[0])
    except (IndexError, ValueError):
        raise RuntimeError('Could not parse temperature output.')


if __name__ == '__main__':
    main()
