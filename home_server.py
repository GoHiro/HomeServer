from aiohttp import web
from aiohttp.web import Application, Response, HTTPOk, run_app
import asyncio
from async_timeout import timeout
import json
import serial
from struct import *
from binascii import *
import ast
import time
import datetime
import match_context
from pprint import pprint


async def get_data_of_specified_key(target_data, key_to_target_data):
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


class OperatingDevice:
    def __init__(self):
        self.current_user = ''
        self.current_name = ''

    async def call_service_behavior(self, service_id, service_name):
        self.current_user = service_id
        self.current_name = service_name
        sequence_list = await self.call_sequence_list(service_id, service_name)
        print(f'Sequence_list: {sequence_list}')
        await home_server.send_sequence_list_to_remocon_by_http(sequence_list)

    async def call_device_name_pared_serial_number(self, current_serial_number):
        matcon = match_context.MatchContext()
        return matcon.get_device_name_pared_serial_number(self.current_user, current_serial_number)

    async def call_sequence_list(self, service_id, service_name):
        matcon = match_context.MatchContext()
        return matcon.call_sequence_list(service_id, service_name)

    async def get_function_list_per_device_sequence(self, device_list):
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

class IrRemocon:
    def __init__(self):
        self.ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=5)
        self._LED = pack('B', 0x69)  # 赤外線リモコンの LED 点灯
        self._RECEIVE = pack('B', 0x72)  # 受信
        self._TRANSMIT = pack('B', 0x74)  # 送信
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

        """async def set_serial_of_function(self, set_serial):
            print('Set serial for sending appliance')
        """

async def http_client(host, port, msg, loop):
    reader, writer = await asyncio.open_connection(
        host, port, loop=loop
    )

    writer.write(msg.encode())
    data = await reader.read()
    print(f'Received: {data.decode()}')
    writer.close()

class HomeServer:
    # サーバとセンサ、家電で同期している変数を保持する
    def __init__(self):
        self.get_data = 0
        self.smart_sensor_port = 0
        self.smart_sensor_condition = 0
        self.smart_appliance_port = 0
        self.smart_appliance_power = ''
        self.smart_appliance_name = ''
        self.smart_appliance_send_param = ''
        self.smart_appliance_mode = ''
        self.service = []
        self.l_value = []

        self.service_name_list = ['A', 'C', 'C_2']
        self.target_service_id_list = [2]
        self.target_service_name_list = ['Concrete_Service_C_8', 'Concrete_Service_C_9']
        self.enviroment_field = {}
        self.specify_condition_table = []
        self.after_condition_list = []
        self.check_after_condition_list = []

        self.kaden = 0
        self.state = 0
        self.channel = 0
        self.temp = 0
        self.rtemp = 0
        self.vol = 0
        self.time = 0
        self.settei = 0
        self.dict = {}

    # サービス.jsonを読み込み、値をlist型の'data'に格納
    async def load_service(self, request):
        print('Load Service List...')
        with open('service.json', mode='r', encoding='utf-8') as f:
            data = json.load(f)
            #target_service_id_list = await self.get_target_service_id()
            condition_dict = []
            time_condition_dict = []
            matcon = match_context.MatchContext()
            for service_id in  self.target_service_id_list:
                device_information = matcon.call_device_information_with_id(service_id)
                await self.set_address_port(device_information)
                await self.sort_service_name_list_by_priority(service_id)
                print(f'target_service_name_list: {self.target_service_name_list}')
                for service_name in self.target_service_name_list:
                    condition_dict.append(matcon.call_packed_condition(service_id,service_name))
                    time_condition_dict.append(matcon.call_time_condition_list(service_id,service_name))
            await self.store_time_condition_dict(time_condition_dict, self.target_service_name_list)
            await self.set_condition(condition_dict)
            # await self.set_time_condition(time_condition_dict)

    async def store_time_condition_dict(self, time_condition_dict, target_service_name_list):
        self.time_condition = time_condition_dict
        self.service_name_list = target_service_name_list
        pprint(self.time_condition)
        self.specify_condition_table = []
        for i in range(len(self.service_name_list)):
            self.specify_condition_table.append(0)

    async def check_time_condition(self, service_name):
        time = self.time_condition[self.service_name_list.index(service_name)]
        now = datetime.datetime.now()
        int_now = int(now.strftime('%Y%m%d%H%M'))
        if time.get('@type') == 'duration':
            start_time = int(now.strftime('%Y%m%d' + time['start']))
            end_time = int(now.strftime('%Y%m%d' + time['end']))
            if int_now >= start_time and int_now <end_time:
                return True
            else:
                return False
        elif time.get('@type') == 'specify':
            if self.specify_condition_table[self.service_name_list.index(service_name)] == 1:
                return True
            else:
                return False
        return False

    async def check_specify_condition_table(self, request):
        await self.check_specify_condition_table2()
        return HTTPOk()

    async def check_specify_condition_table2(self):
        print('check_specify_time')
        specify_matched = False
        for service_name in self.service_name_list:
            time = self.time_condition[self.service_name_list.index(service_name)]
            now = datetime.datetime.now()
            int_now = int(now.strftime('%Y%m%d%H%M'))
            if time.get('@type') == 'specify':
                specify_time = int(now.strftime('%Y%m%d' + time['specify_time']))
                print(specify_time)
                print(int_now)
                print(specify_time + 2)
                if int_now >= specify_time and int_now <= specify_time + 2:
                    self.specify_condition_table[self.service_name_list.index(service_name)] = 1
                    specify_matched = True
                else:
                    self.specify_condition_table[self.service_name_list.index(service_name)] = 0
            else:
                self.specify_condition_table[self.service_name_list.index(service_name)] = 0
        print(f'specify_condition_table:{self.specify_condition_table}')
        if specify_matched:
            self.priority_field = []
            for service_id in self.target_service_id_list:
                for service_name in self.target_service_name_list:
                    await self.compare_enviroment_field_with_condition_equation(service_id, service_name)
        recall_count = 30
        while (recall_count != 0):
            await asyncio.sleep(1)
            recall_count -= 1
        await self.check_specify_condition_table2()

    async def recall_check_specify_condition_table2(self):
        pass

    async def set_address_port(self,device_information):
        print('device_information')
        pprint(device_information)

        self.sensor_host = '169.254.137.173'
        self.sensor_port = '8020'
        self.sensor_host = device_information['dev:DeviceInformation']['dev:SensorHost']
        self.sensor_port = device_information['dev:DeviceInformation']['dev:SensorPort']
        # self.time_notification_host = '169.254.12.61'
        # self.time_notification_port = '8042'
        self.smart_home_device_host = '169.254.12.61'
        self.smart_home_device_port = '8031'
        self.smart_home_device_host = device_information['dev:DeviceInformation']['dev:DeviceHost']
        self.smart_home_device_port = device_information['dev:DeviceInformation']['dev:DevicePort']

    async def sort_service_name_list_by_priority(self,service_id):
        matcon = match_context.MatchContext()
        priority_list = matcon.call_priority_list(service_id, self.target_service_name_list)
        for i in range(len(self.target_service_name_list)):
            for j in range(i+1, len(self.target_service_name_list)):
                if priority_list[i] < priority_list[j]:
                    temp_target_service_name_list = self.target_service_name_list[i]
                    self.target_service_name_list[i] = self.target_service_name_list[j]
                    self.target_service_name_list[j] = temp_target_service_name_list

    async def set_service_value(self):
        await self.set_condition()

    async def set_condition(self,condition_dict):
        print('センサーへ条件の登録を行います')
        sensor_condition = str(condition_dict)
        sensor_condition = await replace_reserved_strings(sensor_condition)
        print(sensor_condition)
        msg = (
            f'GET /sensor/set_condition/{sensor_condition} HTTP/1.1\r\n'
            'Host: localhost:8010\r\n'
            '\r\n'
            '\r\n'
        )
        loop = asyncio.get_running_loop()
        loop.create_task(http_client(self.sensor_host, self.sensor_port, msg, loop))


        return web.Response(text='ok')

    async def send_sequence_list_to_remocon_by_http(self, sequence_list):
        print('send sequence_list to remocon by http')
        host = self.smart_home_device_host
        port = self.smart_home_device_port
        sequence_list = await replace_reserved_strings(str(sequence_list))
        msg = (
            f'GET /device/convey_sequence_list/{sequence_list} HTTP/1.1\r\n'
            'Host: localhost\r\n'
            '\r\n'
            '\r\n'
        )
        loop = asyncio.get_running_loop()
        loop.create_task(http_client(host, port, msg,loop))


    async def send_keyword_to_smart_home_device(self, serial_number, function_name, function_value):
        print('send kwargs to smart_home_device...')
        host = self.smart_home_device_host
        port = self.smart_home_device_port
        serial_number = await replace_reserved_strings(serial_number)
        msg = (
            f'GET /device/convey_keyword/{serial_number}/{function_name}/{function_value} HTTP/1.1\r\n'
            'Host: localhost:8010\r\n'
            '\r\n'
            '\r\n'
        )

        loop = asyncio.get_event_loop()
        loop.run_until_complete(http_client(host, port, msg, loop))
        loop.close()

    # request内部の式'sensor_data'から受信データを取り出す
    async def get_sensor_data(self, request):
        print('get sensor_data ...')
        get_data = request.match_info.get('sensor_data', "Anonymous")
        get_data = await replace_previous_string(get_data)
        get_data = ast.literal_eval(get_data)
        await self.store_enviroment_field(get_data)
        self.check_after_condition_list = []
        self.priority_field = []
        for service_id in self.target_service_id_list:
            for service_name in self.target_service_name_list:
                await self.compare_enviroment_field_with_condition_equation(service_id, service_name)
        for check_after_condition in self.check_after_condition_list:
            await self.check_after_condition(check_after_condition['service_id'], check_after_condition['service_name'])
        return web.Response(text='ok')

    async def start_check_after_condition(self):
        pass

    async def store_enviroment_field(self, get_data):
        print('get_data')
        print(get_data)
        serial_number = get_data['SerialNumber']
        function_name = get_data['FunctionName']
        value = get_data['Value']
        if self.enviroment_field.get(str(serial_number)) not in self.enviroment_field.values():
            temp_dict = {function_name: value}
            self.enviroment_field[serial_number] = temp_dict
            print('enviroment_field')
            print(self.enviroment_field)
        elif self.enviroment_field[serial_number].get(function_name) not in self.enviroment_field.values():
            self.enviroment_field[serial_number][function_name] = value
            print('enviroment_field')
            print(self.enviroment_field)

    async def call_logical_expression(self,service_id, service_name):
        matcon = match_context.MatchContext()
        self.logical_expression = matcon.call_logical_expression(service_id, service_name)
        self.logical_expression = ast.literal_eval(self.logical_expression)
        print(self.logical_expression)

    async def call_condition_equation(self,service_id, service_name):
        matcon = match_context.MatchContext()
        self.condition_equation = matcon.call_condition_equation(service_id, service_name)
        print(self.condition_equation)

    async def compare_enviroment_field_with_condition_equation(self,service_id, service_name):
        await self.call_logical_expression(service_id, service_name)
        await self.call_condition_equation(service_id, service_name)
        check_list = await self.check_true_primitive_condition()
        if await self.check_logical_expression_by_check_list(check_list):
            print(check_list)
            #service_id = 2
            #service_name = 'Concrete_Service_C'

            if await self.check_time_condition(service_name):
                # append priority filter composition with purpose and priority
                if await self.check_purpose_and_priority_with_priority_field(service_id, service_name):
                    await self.service_name_append_to_check_after_condition_list(service_id, service_name)
                    await self.service_execute(service_id, service_name)

    async def check_purpose_and_priority_with_priority_field(self, service_id, service_name):
        # fixme: need to reverse priority sort -> maybe ok
        matcon = match_context.MatchContext()
        purpose_priority_dict = matcon.call_purpose_and_priority(service_id, service_name)
        priority_pass = True
        if self.priority_field:
            for priority_field in self.priority_field:
                if priority_field['Purpose'] == purpose_priority_dict['Purpose'] and priority_field['Priority'] >= purpose_priority_dict['Priority']:
                    priority_pass = False
        elif not self.priority_field:
            self.priority_field.append(purpose_priority_dict)
        if priority_pass:
            return True
        else:
            return False



    async def service_name_append_to_check_after_condition_list(self, service_id, service_name):
        appended_dict = {'service_id': service_id,
                         'service_name': service_name}
        if appended_dict not in self.check_after_condition_list:
            self.check_after_condition_list.append(appended_dict)

    async def check_after_condition(self, service_id, service_name):
        matcon = match_context.MatchContext()
        if matcon.call_check_service_has_after_condition(service_id, service_name):
            if await self.check_same_service_name_in_after_condition(service_name):
                after_condition = await self.call_load_after_condition(service_id, service_name)
                await self.add_active_after_condition_list(after_condition)

    async def call_load_after_condition(self, service_id, service_name):
        matcon = match_context.MatchContext()
        return matcon.call_load_after_condition(service_id, service_name)

    async def check_same_service_name_in_after_condition(self, service_name):
        isthere = False
        if self.after_condition_list:
            for after_condition in self.after_condition_list:
                if after_condition['ServiceName'] == service_name:
                    isthere = True
                    break
        if not isthere:
            return True
        else:
            return False

    async def add_active_after_condition_list(self, after_condition):
        self.after_condition_list.append(after_condition)
        if len(self.after_condition_list) == 1:
            await self.decision_timer()

    async def decision_timer(self):
        while(len(self.after_condition_list) != 0):
            current_ordinal_list = []
            for ordinal in range(len(self.after_condition_list)):
                self.after_condition_list[ordinal]['@decision_time'] = str(int(self.after_condition_list[ordinal]['@decision_time']) - 1)

                print(self.after_condition_list[ordinal]['@decision_time'])
                if int(self.after_condition_list[ordinal]['@decision_time']) <= 0:
                    await self.get_current_sensor_value_from_smart_sensor()
                    await asyncio.sleep(1)
                    await self.compare_after_condition_with_current_sensor_value(self.after_condition_list[ordinal])
                    current_ordinal_list.append(ordinal)
            await asyncio.sleep(1)
            if current_ordinal_list:
                for ordinal in current_ordinal_list:
                    self.after_condition_list.pop(ordinal)

    async def compare_after_condition_with_current_sensor_value(self, after_condition):
        # self.current_sensor_value
        key_to_context_in_after_condition = ['ns4:ContextList', 'ns4:Context', 'ns4:DeviceList', 'ns4:Device']
        after_condition_context = await get_data_of_specified_key(after_condition,
                                                            key_to_context_in_after_condition)
        after_condition_serial_number = after_condition_context['ns4:SerialNumber']
        after_condition_function_name = after_condition_context['ns4:Function']['ns4:FunctionName']
        after_condition_value = after_condition_context['ns4:Value']
        after_condition_value_equation = await self.check_after_condition_value_type(after_condition_value)
        current_sensor_value = await self.find_sensor_value_matched_with_after_condition(after_condition_serial_number,after_condition_function_name)
        if current_sensor_value != None:
            if eval(str(current_sensor_value+after_condition_value_equation)):
                await self.after_condition_matched(after_condition['ServiceName'])
            else:
                await self.after_condition_not_matched(after_condition['ServiceName'])
        else:
            print(f'not found the value corresponding to x/after_condition_equation: {after_condition_value_equation}')

    async def after_condition_matched(self,matched_service_name_for_after_condition):
        # print(f'matched_service_name_for_after_condition: {matched_service_name_for_after_condition}')
        pass

    async def after_condition_not_matched(self, not_matched_service_name_for_after_condition):
        print('caution: may not be working properly')
        print(f'not_matched_service_name_for_after_condition: {not_matched_service_name_for_after_condition}')

    async def find_sensor_value_matched_with_after_condition(self, serial_number, function_name):
        value = None
        for sensor_value in self.current_sensor_value:
            if sensor_value.get(serial_number):
                if sensor_value[serial_number].get(function_name):
                    value = sensor_value[serial_number][function_name]
                    break
        return value

    async def check_after_condition_value_type(self, after_condition_value):
        after_condition_value_type = await self.type_check(after_condition_value['@type'])
        after_condition_value_text = await self.text_check(after_condition_value['#text'])
        return after_condition_value_type + after_condition_value_text

    async def type_check(self, after_condition_value_type):
        if after_condition_value_type == 'upper':
            type = '>='
        elif after_condition_value_type == 'equal':
            type = '=='
        elif after_condition_value_type == 'lower':
            type = '<'
        return type

    async def text_check(self, after_condition_value_text):
        if after_condition_value_text == 'TRUE':
            text = 'True'
        elif after_condition_value_text == 'FALSE':
            text = 'False'
        else:
            text = after_condition_value_text
        return text

    async def get_current_sensor_value_from_smart_sensor(self):
        # todo:get_current_sensor_value_from_smart_sensor
        print('get current sensor value...')
        host = self.sensor_host
        port = self.sensor_port
        msg = (
            f'GET /sensor/get_current_sensor_value_from_smart_sensor HTTP/1.1\r\n'
            'Host: localhost:8010\r\n'
            '\r\n'
            '\r\n'
        )

        loop = asyncio.get_running_loop()
        loop.create_task(http_client(host, port, msg, loop))

    async def service_execute(self, service_id, service_name):
        print(f'Service {service_id} activate...')
        OpeDev = OperatingDevice()
        await OpeDev.call_service_behavior(service_id, service_name)

    async def count_string_of_logical_expression(self):
        logical_expression = self.logical_expression['ConditionEquation']
        string_count = len(logical_expression) + 1
        assert isinstance(string_count, int)
        return string_count

    async def check_logical_expression_by_check_list(self, check_list):
        logical_expression = self.logical_expression['ConditionEquation']
        for i in range(await self.count_string_of_logical_expression()):
            if str(i) in str(logical_expression):
                if check_list[i] == '1':
                    logical_expression = logical_expression.replace(f'{str(i)}', '1')
                elif check_list[i] == '0':
                    logical_expression = logical_expression.replace(f'{str(i)}', '0')
        logical_expression = logical_expression.replace('∧', '&')
        logical_expression = logical_expression.replace('∨', '|')
        print('-------------------------------------------------------')
        print(f'logical_expression: {logical_expression}')
        return eval(logical_expression)

    async def check_true_primitive_condition(self):
        # T/F in Caa' premitive_condition and Tem' premitive_condition
        # Checking service_condition is not perfect
        check_list = [0] * (await self.count_string_of_logical_expression())
        for id in range(await self.count_string_of_logical_expression()):
            print('id')
            print(id)
            print('check_list')
            print(check_list)
            if await self.find_primitive_condition_contained_id(id):
                if await self.check_true_primitive_condition_per_id(id):
                    check_list[id] = '1'
                else:
                    check_list[id] = '0'
            else:
                check_list[id] = '0'
        print(f'check_list: {check_list}')
        return check_list

    async def find_primitive_condition_contained_id(self, id):
        logical_expression = str(self.logical_expression)
        if str(id) in logical_expression:
            return True
        else:
            return False

    async def check_true_primitive_condition_per_id(self, id):
        primitive_condition_per_id = await self.get_primitive_condition_per_id(id)
        print('primitive_condition_per_id')
        print(primitive_condition_per_id)
        serial_number = primitive_condition_per_id['SerialNumber']
        function_name = primitive_condition_per_id['FunctionName']
        print('self.enviroment_field')
        print(self.enviroment_field)
        environment_value = await self.get_enviroment_value_from_serial_number(self.enviroment_field, serial_number)
        if environment_value is None:
            return False
        elif environment_value is not None:
            print('enviroment_value')
            print(environment_value)
            assert isinstance(environment_value,dict), 'enviroment_value is not dict'
            environment_value = await self.get_enviroment_value_from_function_name(environment_value, function_name)
            if environment_value is None:
                return False
            elif environment_value is not None:
                expression = environment_value + primitive_condition_per_id['Value']
                print('expression')
                print(expression)
                if eval(expression):
                    return True
                else:
                    return False

    async def get_enviroment_value_from_serial_number(self,enviroment_value,serial_number):
        return enviroment_value.get(serial_number)

    async def get_enviroment_value_from_function_name(self,enviroment_value,function_name):
        return enviroment_value.get(function_name)

    async def get_primitive_condition_per_id(self, id):
        condition_equation = self.condition_equation
        primitive_condition_per_id = condition_equation[f'{id}']
        return primitive_condition_per_id

    async def translate_condition_equation(self):
        condition_equation = str(self.condition_equation['ConditionEquation'])
        for i in range(len(condition_equation)):
            condition_equation = condition_equation.replace(f'{i}', 'id' + f'{i}')
        return condition_equation

    async def get_enviroment_value(self):
        serial_number = self.condition_equation['SerialNumber']
        function_name = self.condition_equation['FunctionName']
        enviroment_value = self.enviroment_field[serial_number][function_name]
        return enviroment_value

    # cronで一定時間ごとにサービスの条件を比較する、いらない気がしてきた
    async def cron_check_service_condition(self, request):
        print('条件:' + str(self.smart_sensor_condition) + '<= データ:' + str(self.get_data))
        if self.smart_sensor_condition <= self.get_data:
            print(float(self.get_data))
            print('条件を満たしました、サービスを実行します')
            await self.appliance_power_switch()
        else:
            print('条件を満たしていません')

    async def appliance_power_switch(self):
        host = '127.0.0.1'
        port = self.smart_appliance_port
        appliance_power = self.smart_appliance_power
        print('家電へリクエストを送信します')
        msg = (
            f'GET /appliance/appliance_power_switch/{appliance_power} HTTP/1.1\r\n'
            'Host: localhost:8010\r\n'
            '\r\n'
            '\r\n'
        )
        self.diction(appliance_power)
        loop = asyncio.get_event_loop()
        await loop.create_task(http_client(host, port, msg, loop))
        return web.Response(text='ok')

    async def set_current_sensor_value(self, request):
        current_sensor_value = request.match_info.get('sensor_data', "Anonymous")
        current_sensor_value = await replace_previous_string(current_sensor_value)
        current_sensor_value = ast.literal_eval(current_sensor_value)
        self.current_sensor_value = current_sensor_value
        return web.Response(text='ok')

    def main(self):
        print('Starting Home Server ...')
        app = web.Application()
        app.router.add_get('/server/get_sensor_data/{sensor_data}', self.get_sensor_data)
        app.router.add_get('/server/load_service', self.load_service)
        app.router.add_get('/server/check_specify_condition_table',self.check_specify_condition_table)
        app.router.add_get('/server/sensor_value_for_after_condition/{sensor_data}', self.set_current_sensor_value)
        web.run_app(app, host='169.254.12.61', port=8010)

if __name__ == '__main__':
    home_server = HomeServer()
    home_server.main()
