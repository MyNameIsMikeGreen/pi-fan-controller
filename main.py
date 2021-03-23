import logging
import subprocess
import time

from gpiozero import OutputDevice

LOG_LEVEL = logging.INFO

ON_THRESHOLD_CELSIUS = 65   # Temperature at which to start the fan
OFF_THRESHOLD_CELSIUS = 50  # Temperature at which to stop the fan
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
    logger = create_logger()
    logger.info("Fan controller started.")
    if OFF_THRESHOLD_CELSIUS >= ON_THRESHOLD_CELSIUS:
        raise RuntimeError('OFF_THRESHOLD_CELSIUS must be less than ON_THRESHOLD_CELSIUS')

    fan = Fan(GPIO_FAN)

    while True:
        temperature = get_temperature()
        logger.debug(f"Measured temperature: {temperature}C")
        if temperature >= ON_THRESHOLD_CELSIUS:
            if fan.is_off():
                logger.info(f"Temperature has risen above threshold of {ON_THRESHOLD_CELSIUS}, turning fan on...")
                fan.turn_on()

        elif temperature <= OFF_THRESHOLD_CELSIUS:
            if fan.is_on():
                logger.info(f"Temperature has fallen below threshold of {OFF_THRESHOLD_CELSIUS}, turning fan off...")
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


def create_logger():
    logger = logging.getLogger('pi_fan_controller')
    logger.setLevel(LOG_LEVEL)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s | %(name)s | %(levelname)s | %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger


if __name__ == '__main__':
    main()
