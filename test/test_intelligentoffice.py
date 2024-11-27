import unittest
from datetime import datetime
from unittest.mock import patch, Mock, PropertyMock
import mock.GPIO as GPIO
from mock.SDL_DS3231 import SDL_DS3231
from mock.adafruit_veml7700 import VEML7700
from src.intelligentoffice import IntelligentOffice, IntelligentOfficeError


class TestIntelligentOffice(unittest.TestCase):

    @patch.object(GPIO,"input")
    def test_check_quadrant_occupancy(self, mock_distance_sensor: Mock):
        mock_distance_sensor.side_effect= [True, True, False, True]
        system = IntelligentOffice()
        occupied = 0
        for sensor in [system.INFRARED_PIN1, system.INFRARED_PIN2, system.INFRARED_PIN3, system.INFRARED_PIN4]:
            if system.check_quadrant_occupancy(sensor):
                occupied += 1
        self.assertEqual(occupied, 3)

    @patch.object(GPIO, "input")
    def test_check_quadrant_occupancy_invalid_pin(self, mock_distance_sensor: Mock):
        mock_distance_sensor.return_value = False
        system = IntelligentOffice()
        self.assertRaises(IntelligentOfficeError, system.check_quadrant_occupancy, 100)