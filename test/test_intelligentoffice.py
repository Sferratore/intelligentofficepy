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

    @patch.object(IntelligentOffice, "change_servo_angle")
    @patch.object(SDL_DS3231, "read_datetime")
    def test_manage_blinds_based_on_time_when_time_between_8_and_20_in_weekday(self, mock_datetime: Mock, mock_output: Mock):
        mock_datetime.return_value = datetime(2024, 11, 11, 8, 0)
        system = IntelligentOffice()
        system.manage_blinds_based_on_time()
        mock_output.assert_called_once_with(12)
        self.assertTrue(system.blinds_open)

    @patch.object(IntelligentOffice, "change_servo_angle")
    @patch.object(SDL_DS3231, "read_datetime")
    def test_manage_blinds_based_on_time_when_time_not_between_8_and_20_in_weekday(self, mock_datetime: Mock, mock_output: Mock):
        mock_datetime.return_value = datetime(2024, 11, 11, 7, 59)
        system = IntelligentOffice()
        system.manage_blinds_based_on_time()
        mock_output.assert_called_once_with(0)
        self.assertTrue(not system.blinds_open)

    @patch.object(IntelligentOffice, "change_servo_angle")
    @patch.object(SDL_DS3231, "read_datetime")
    def test_manage_blinds_based_on_time_when_time_between_8_and_20_in_weekends(self, mock_datetime: Mock, mock_output: Mock):
        mock_datetime.return_value = datetime(2024, 11, 10, 11, 59)
        system = IntelligentOffice()
        system.manage_blinds_based_on_time()
        mock_output.assert_called_once_with(0)
        self.assertTrue(not system.blinds_open)

    @patch.object(IntelligentOffice, "change_servo_angle")
    @patch.object(SDL_DS3231, "read_datetime")
    def test_manage_blinds_based_on_time_when_time_not_between_8_and_20_in_weekends(self, mock_datetime: Mock, mock_output: Mock):
        mock_datetime.return_value = datetime(2024, 11, 10, 1, 59)
        system = IntelligentOffice()
        system.manage_blinds_based_on_time()
        mock_output.assert_called_once_with(0)
        self.assertTrue(not system.blinds_open)

    @patch.object(IntelligentOffice, "check_quadrant_occupancy")
    @patch.object(VEML7700, "lux", new_callable=PropertyMock)
    @patch.object(GPIO, "output")
    def test_manage_light_level_when_not_enough_light(self, mock_output: Mock, mock_light: Mock, mock_occ: Mock):
        mock_light.return_value = 499
        mock_occ.side_effect = [True, True, False, False]
        system = IntelligentOffice()
        system.manage_light_level()
        mock_output.assert_called_once_with(system.LED_PIN, True)
        self.assertTrue(system.light_on)

    @patch.object(VEML7700, "lux", new_callable=PropertyMock)
    @patch.object(GPIO, "output")
    def test_manage_light_level_when_more_than_enough_light(self, mock_output: Mock, mock_light: Mock):
        mock_light.return_value = 551
        system = IntelligentOffice()
        system.manage_light_level()
        mock_output.assert_called_once_with(system.LED_PIN, False)
        self.assertTrue(not system.light_on)

    @patch.object(GPIO, "output")
    @patch.object(IntelligentOffice, "check_quadrant_occupancy")
    @patch.object(VEML7700, "lux", new_callable=PropertyMock)
    def test_manage_light_level_when_room_not_occupied_and_not_enough_light(self, mock_light: Mock, mock_occupancy: Mock,
                                                                        mock_output: Mock):
        mock_occupancy.side_effect = [False, False, False, False]
        mock_light.return_value = 499
        system = IntelligentOffice()
        system.manage_light_level()
        mock_output.assert_called_once_with(system.LED_PIN, False)
        self.assertTrue(not system.light_on)

    @patch.object(GPIO, "output")
    @patch.object(GPIO, "input")
    def test_monitor_air_quality_when_smoke(self, mock_smoke_sensor, mock_buzzer):
        mock_smoke_sensor.return_value = True
        system = IntelligentOffice()
        system.monitor_air_quality()
        mock_buzzer.assert_called_once_with(system.BUZZER_PIN, True)
        self.assertTrue(system.buzzer_on)

    @patch.object(GPIO, "output")
    @patch.object(GPIO, "input")
    def test_monitor_air_quality_when_not_smoke(self, mock_smoke_sensor, mock_buzzer):
        mock_smoke_sensor.return_value = False
        system = IntelligentOffice()
        system.monitor_air_quality()
        mock_buzzer.assert_called_once_with(system.BUZZER_PIN, False)
        self.assertTrue(not system.buzzer_on)