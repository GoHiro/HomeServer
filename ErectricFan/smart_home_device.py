from aiohttp import web
import asyncio
import serial
from struct import *
from binascii import *
import ast
import os
import time
import json
import ast
from pprint import pprint as pprint

async def get_data_of_specified_key(target_data: object, key_to_target_data: object) -> object:
    for key in key_to_target_data:
        target_data = target_data[key]
    return target_data

async def replace_reserved_strings(res_str):
    reserved_to_unreserved = {'{': 'above_curly', ':': 'middle_colon',
                              '}': 'below_curly', "'": 'top_quote', ',': 'under_comma',
                              '@': 'attribute_at', '#': 'text_sharp', ' ': 'margin_space',
                              '[': 'above_list', ']': 'below_list'}
    for reserved, unreserved in reserved_to_unreserved.items():
        res_str = res_str.replace(f'{reserved}', f'{unreserved}')
    return res_str

async def replace_previous_string(res_str):
    # original string replaces to usable string on arrangement of http
    unreserved_to_previous_string = {'above_curly': '{', 'middle_colon': ':',
                                     'below_curly': '}', 'top_quote': "'", 'under_comma': ',',
                                     'attribute_at': '@', 'text_sharp': '#', 'margin_space': ' ',
                                     'above_list': '[', 'below_list': ']'}
    for unreserved, previous in unreserved_to_previous_string.items():
        res_str = res_str.replace(f'{unreserved}', f'{previous}')
    return res_str


class SerialFinder:
    def __init__(self):
        self.function_serial_dict = {'IRLight': {'OperatingStatus': {'ON': 'ffffff070000e03fc03f807f0000fc0300e03f0000fe0100f00fe01fc03f00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000fcffff0f0000807f80ff00ff0100f00f00807f0000fc0300e03fc03f807f00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000fcffff0f0000807f00ff00ff0100f00f00807f0000fc0300e03fc07f807f00000000000000000000000000000000',
                                                                     'OFF': 'ffffff070000e03fc03f0000fe03fc07f80700c07f807f0000fc0700c03f00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000fcffff0f0000c07f80ff0000f807f80ff01f0080ff00ff0100f00f00807f00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000fcffff0f0000c07f80ff0000fc07f80ff00f0080ff00ff0000f80f00807f00000000000000000000000000000000'}},
                                     'ErectricFan': {'OperatingStatus': {'Switch': 'ffff7f807f00803fc03fc01f00e01fe00fe00ff007f007f007f007f807f803f803fc01fc010000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000'},
                                                     'OperatingMode': {'Switch': '53ffff7f807f00803fc03fc01f00e01fe00fe00ff00700f007f00700f803f80300fc01fe01fe00007f00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000ffff7f803f00c03fc03fc01f00e00fe00ff00ff00700f807f80300f803fc0300fc01fe00fe00007f0000000000000000000000000000000000000000000000000000000000000000000000'},
                                                     'TemperatureSettingValue': {'Upper': 'ffff7f807f00803fc03fc03f00e01fe00fe00ff007f00700f00700f80300fc0100fe01fe00007f007f000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000feff7f807f00803fc03fc01f00e01fe00ff00ff007f00700f80700f80300fc0100fe01fe00007f007f0000000000000000000000000000000000000000000000000000000000000000000000',
                                                                                 'lower': 'ffff7f807f00803fc03fc01f00e01fe00fe00ff00700f00700f803f803f80300fc0100fe00fe007f000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000c0ffff1fe00f00f00ff00ff00700f803f803fc03fc0100fe0100fe00fe00ff00007f00803fc03fc01f000000000000000000000000000000000000000000000000000000000000000000000000'},
                                                     'FanSpeed': {'Upper': '53ffff7f807f00803fc03fc01f00e01fe00fe00ff007f00700f007f80300f803fc0100fe01fe00007f000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000c0ffff1fe00f00f00ff00ff00700f803f803fc03fc01fc0100fe00fe0000ff007f00803f803f00c01f0000000000000000000000000000000000000000000000000000000000000000000000',
                                                                  'lower': 'ffff7f807f00803f803fc01f00e01fe00fe00ff00700f00700f80300f80300fc0100fe0000ff00807f803f000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000feff7f007f00803f803fc03f00c01fe00fe00ff00700f00700f80700f80300fc0100fe0000ff00007f803f00000000000000000000000000000000000000000000000000000000'}}}

        # current_device_state will change that load from 'current_device_state.json'
        self.current_device_state = {'Fan C': {'OperatingStatus': 'ON',
                                               'OperatingMode': 'Stable',
                                               'TemperatureSettingValue': '37',
                                               'FanSpeed': '5'}}

    async def catch_keyword(self, serial_number, function_name, function_value):
        self.serial_number_in_current_sequence = serial_number
        self.function_name = function_name
        self.function_value = function_value

        print(f'serial_number: {serial_number}')
        print(type(serial_number))
        print(f'function_name: {function_name}')
        print(type(function_name))
        print(f'function_value: {function_value}')
        print(type(function_value))

        if function_value == await self.get_current_device_state(function_name):
            print('current_state equal function_name')
        elif not function_value.isdecimal():
            await self.call_strings_behavior(function_name)
        elif function_value.isdecimal():
            await self.call_integer_behavior()

    async def catch_sequence_list(self, sequence_list):
        print('find operating serial in sequence_list')
        pprint(f'current_device_state: {self.current_device_state}')
        await self.get_function_list_per_device_sequence(sequence_list)
        pprint(f'current_device_state: {self.current_device_state}')

    async def get_function_list_per_device_sequence(self, sequence_list):
        device_list = sequence_list
        for device_seq in device_list:
            self.serial_number_in_current_sequence = device_seq['ns3:SerialNumber']
            function_list = device_seq['ns3:FunctionList']['ns3:Function']
            await self.get_function_per_function_sequence(function_list)

    async def get_function_per_function_sequence(self, function_list):
        for func_seq in function_list:
            function_name = func_seq['ns3:FunctionName']
            function_value = func_seq['ns3:Value']
            print(f'function_name: {function_name}')
            print(f'function_value: {function_value}')

            if function_value == await self.get_current_device_state(function_name):
                continue
            elif not function_value.isdecimal():
                await self.call_strings_behavior(function_name)
                await self.update_current_device_state(function_name, function_value)
            elif function_value.isdecimal():
                await self.call_integer_behavior(function_value, function_name)
                await self.update_current_device_state(function_name, function_value)

    async def get_current_device_state(self, function_name):
        key_to_current_device_state = [self.serial_number_in_current_sequence, function_name]
        current_device_state = self.current_device_state
        for key in key_to_current_device_state:
            current_device_state = current_device_state[key]
        # print(f'current_dvice_state: {current_device_state}')
        return current_device_state

    async def update_current_device_state(self, function_name, function_value):
        self.current_device_state[self.serial_number_in_current_sequence][function_name] = function_value


    async def get_device_name_pared_serial_number(self):
        device_information = ConRec.device_information
        return device_information['dev:DeviceName']

    async def call_strings_behavior(self, function_name):
        set_serial = await self.get_function_serial_of_current_serial_number(function_name)
        # await IrRemocon.set_serial_of_function(set_serial)
        IRC = IrRemocon()
        await IRC.send_serial_for_appliance(set_serial)
        time.sleep(1)

    async def get_integer_function_serial_of_current_serial_number(self, function_name, up_or_low):
        checked_dict = self.function_serial_dict
        self.current_device_name = await self.get_device_name_pared_serial_number()
        serial_key = [self.current_device_name, function_name]
        # print(serial_key)
        # print(checked_dict)

        for key in serial_key:
            checked_dict = checked_dict[key]
        checked_dict = checked_dict[up_or_low]
        return checked_dict

    async def get_function_serial_of_current_serial_number(self, function_name):
        checked_dict = self.function_serial_dict
        self.current_device_name = await self.get_device_name_pared_serial_number()
        serial_key = [self.current_device_name, function_name]
        # print(serial_key)
        # print(checked_dict)

        for key in serial_key:
            checked_dict = checked_dict[key]
        return checked_dict

    async def tell_operating_serial(self, function_name):
        set_serial = await self.get_function_serial_of_current_serial_number(function_name)
        # await IrRemocon.set_serial_of_function(set_serial)
        IRC = IrRemocon()
        await IRC.send_serial_for_appliance(set_serial)
        time.sleep(1)

    async def call_integer_behavior(self, function_value, function_name):
        current_state_value = int(await self.get_current_device_state(function_name))
        function_value = int(function_value)
        if current_state_value <= function_value:
            set_serial = await self.get_integer_function_serial_of_current_serial_number(function_name, 'Upper')
        elif current_state_value > function_value:
            set_serial = await self.get_integer_function_serial_of_current_serial_number(function_name, 'lower')
        # await IrRemocon.set_serial_of_function(set_serial)
        difference = current_state_value - function_value
        send_count = abs(difference)
        IRC = IrRemocon()
        while True:
            if send_count <= 0:
                break
            send_count -= 1
            await IRC.send_serial_for_appliance(set_serial)
            time.sleep(1)

class IrRemocon:
    def __init__(self):
        self.ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=5)
        self._LED = pack('B', 0x69)
        self._RECEIVE = pack('B', 0x72)
        self._TRANSMIT = pack('B', 0x74)
        self.ch1 = pack('B', 0x31)  # A (黄)
        self.ch2 = pack('B', 0x32)  # A (黒)
        self.ch3 = pack('B', 0x33)  # B (黄)
        self.ch4 = pack('B', 0x34)  # B (黒)
        self.r_data = 0  # 受信する際の変数

    def led(self):
        """LED を点灯させる"""

        self.ser.write(self._LED)
        self.ser.read()  # 0x4f

    def receive(self) -> bytes:
        """赤外線を受信する"""

        print('receiving...' + str(self.r_data))
        self.ser.write(self._RECEIVE)
        self.ser.read(1)  # 0x59
        self.ser.read(1)  # 0x53

        self.r_data = hexlify(self.ser.read(240))  # このデータを送信(リモコンで信号送信)
        self.ser.read(1)

        print('received:' + str(self.r_data))  # 0x45
        return self.r_data

    def transmit(self, hex_data: bytes, channel: bytes):
        """ 赤外線を送信する(send_data, send_ch)"""

        bin_data = a2b_hex(hex_data)
        self.ser.write(self._TRANSMIT)
        self.ser.read(1)  # 0x59
        self.ser.write(channel)  # チャンネルの指定
        self.ser.read(1)  # 0x59
        self.ser.write(bin_data)  # データの送信
        self.ser.read(1)  # 0x45

    def __enter__(self):
        return self

    def __exit__(self, *args):
        print('Serial is closed')
        self.ser.close()

    async def send_serial_for_appliance(self, set_serial):
        print(f'serial send to appliance: {set_serial}')
        self.transmit(set_serial, self.ch3)


class ConveyReceivingData:
    def __init__(self):
        self.device_information = {}
        self.home_server_host = '169.254.12.61'
        self.home_server_port = '8010'

    async def convey_keyword(self, request):
        print('convey_value')
        serial_number = request.match_info.get('serial_number', "Anonymous")
        serial_number = await replace_previous_string(serial_number)
        function_name = request.match_info.get('function_name', "Anonymous")
        function_value = request.match_info.get('function_value', "Anonymous")
        await SerialFinder.catch_keyword(serial_number=serial_number, function_name=function_name, function_value=function_value)

        return web.Response(text='ok')

    async def convey_sequence_list(self, request):
        print('convey_sequence_list')
        sequence_list = request.match_info.get('sequence_list', "Anonymous")
        sequence_list = await replace_previous_string(sequence_list)
        sequence_list = ast.literal_eval(sequence_list)
        await SerialFinder.catch_sequence_list(sequence_list)

        return web.Response(text='ok')

    """async def load_device_information(self):
        with open()
        self.device_information"""

    async def http_client(self, host, port, msg, loop):
        reader, writer = await asyncio.open_connection(
            host, port, loop=loop
        )

        writer.write(msg.encode())
        data = await reader.read()
        print(f'Received: {data.decode()}')
        writer.close()

    async def send_device_information(self):
        print('send device_information to home_server')
        host = self.home_server_host
        port = self.home_server_port

        device_information = self.device_information
        matcon = match_context.MatchContext()
        condition_dict = matcon.call_packed_condition(device_information)
        sensor_condition = str(condition_dict)
        sensor_condition = await replace_reserved_strings(sensor_condition)
        print(sensor_condition)
        msg = (
            f'GET /sensor/set_condition/{sensor_condition} HTTP/1.1\r\n'
            'Host: localhost:8010\r\n'
            '\r\n'
            '\r\n'
        )

        loop = asyncio.get_event_loop()
        # loop.create_task(self.http_client(host, port, msg, loop))
        loop.run_until_complete(self.http_client(host, port, msg, loop))
        loop.close()
        return web.Response(text='ok')

    def load_device_information(self):
        path_to_cwd = os.getcwd()
        with open(path_to_cwd + '/DeviceInformation.json',
                  mode='r', encoding='utf-8') as device_information:
            self.device_information = json.load(device_information)

    def main(self):
        print('Starting Smart Home Device ...')
        self.load_device_information()

        app = web.Application()
        app.router.add_get('/device/convey_keyword/{serial_number}/{function_name}/{function_value}',
                           self.convey_keyword)
        app.router.add_get('/device/convey_sequence_list/{sequence_list}', self.convey_sequence_list)
        web.run_app(app, host='169.254.12.61', port=8031)


SerialFinder = SerialFinder()


if __name__ == '__main__':
    ConRec = ConveyReceivingData()
    ConRec.main()

