import time

DEPLOYMENT = False  # This variable is to understand whether you are deploying on the actual hardware

try:
    import RPi.GPIO as GPIO
    import SDL_DS3231
    import board
    import adafruit_veml7700
    DEPLOYMENT = True
except:
    import mock.GPIO as GPIO
    import mock.SDL_DS3231 as SDL_DS3231
    import mock.board as board
    import mock.adafruit_veml7700 as adafruit_veml7700


class IntelligentOffice:

    INFRARED_PIN1 = 11 # First infrared distance sensor pin
    INFRARED_PIN2 = 12 # Second infrared distance sensor pin
    INFRARED_PIN3 = 13 # Third infrared distance sensor pin
    INFRARED_PIN4 = 15 # Fourth infrared distance sensor pin
    SERVO_PIN = 18 # Servo motor pin
    LED_PIN = 29 # Light pin
    GAS_PIN = 31 # Gas/smoke sensor pin
    BUZZER_PIN = 36 # Active buzzer pin

    def __init__(self):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        GPIO.setup(self.INFRARED_PIN1, GPIO.IN)
        GPIO.setup(self.INFRARED_PIN2, GPIO.IN)
        GPIO.setup(self.INFRARED_PIN3, GPIO.IN)
        GPIO.setup(self.INFRARED_PIN4, GPIO.IN)
        GPIO.setup(self.SERVO_PIN, GPIO.OUT)
        GPIO.setup(self.LED_PIN, GPIO.OUT)
        GPIO.setup(self.GAS_PIN, GPIO.IN)
        GPIO.setup(self.BUZZER_PIN, GPIO.OUT)

        self.rtc = SDL_DS3231.SDL_DS3231(1, 0x68) # rtc

        self.servo = GPIO.PWM(self.SERVO_PIN, 50)
        self.servo.start(2)  # Starts generating PWM on the pin with a duty cycle equal to 2% (corresponding to 0 degree)
        if DEPLOYMENT:  # Sleep only if you are deploying on the actual hardware
            time.sleep(1)  # Waits 1 second so that the servo motor has time to make the turn
        self.servo.ChangeDutyCycle(0)  # Sets duty cycle equal to 0% (corresponding to a low signal)

        i2c = board.I2C()
        self.ambient_light_sensor = adafruit_veml7700.VEML7700(i2c, 0x10) # ambient light sensor

        self.blinds_open = False
        self.light_on = False
        self.buzzer_on = False

    def check_quadrant_occupancy(self, pin: int) -> bool:
        if pin in [self.INFRARED_PIN1, self.INFRARED_PIN2, self.INFRARED_PIN3, self.INFRARED_PIN4]:
            return GPIO.input(pin)
        else:
            raise IntelligentOfficeError

    def manage_blinds_based_on_time(self) -> None:
        # To be implemented
        pass

    def manage_light_level(self) -> None:
        # To be implemented
        pass


    def monitor_air_quality(self) -> None:
        # To be implemented
        pass

    def change_servo_angle(self, duty_cycle):
        """
        Changes the servo motor's angle by passing it the corresponding PWM duty cycle
        :param duty_cycle: the PWM duty cycle (it's a percentage value)
        """
        self.servo.ChangeDutyCycle(duty_cycle)
        if DEPLOYMENT:  # Sleep only if you are deploying on the actual hardware
            time.sleep(1)
        self.servo.ChangeDutyCycle(0)


class IntelligentOfficeError(Exception):
    pass
