from aiohttp import web
import asyncio
import json
import serial
from struct import *
from binascii import *
import ast
import time
import match_context


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
        self.target_service_name_list = ['Concrete_Service_C_2','Concrete_Service_C_3']
        self.enviroment_field = {}
        self.smart_home_device_host = '169.254.12.61'
        self.smart_home_device_port = 8031

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
            matcon = match_context.MatchContext()
            for service_id in  self.target_service_id_list:
                for service_name in self.target_service_name_list:
                    condition_dict.append(matcon.call_packed_condition(service_id,service_name))
            await self.set_condition(condition_dict)

    async def set_service_value(self):
        await self.set_condition()

    async def set_condition(self,condition_dict):
        print('センサーへ条件の登録を行います')
        host = '169.254.137.173'
        port = '8020'
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
        loop.run_until_complete(http_client(host, port, msg, loop))
        loop.close()
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
        loop = asyncio.get_event_loop()
        loop.run_until_complete(http_client(host, port, msg,loop))
        loop.close()

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
        for service_id in self.target_service_id_list:
            for service_name in self.target_service_name_list:
                await self.compare_enviroment_field_with_condition_equation(service_id, service_name)
        return web.Response(text='ok')

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
            await self.service_execute(service_id, service_name)

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
        # fixme
        primitive_condition_per_id = await self.get_primitive_condition_per_id(id)
        print('primitive_condition_per_id')
        print(primitive_condition_per_id)
        serial_number = primitive_condition_per_id['SerialNumber']
        function_name = primitive_condition_per_id['FunctionName']
        print('self.enviroment_field')
        print(self.enviroment_field)
        enviroment_value = await self.get_enviroment_value_from_serial_number(self.enviroment_field, serial_number)
        if enviroment_value is None:
            return False
        elif enviroment_value is not None:
            print('enviroment_value')
            print(enviroment_value)
            assert isinstance(enviroment_value,dict), 'enviroment_value is not dict'
            enviroment_value = await self.get_enviroment_value_from_function_name(enviroment_value, function_name)
            if enviroment_value is None:
                return False
            elif enviroment_value is not None:
                expression = enviroment_value + primitive_condition_per_id['Value']
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

    def main(self):
        print('Starting Home Server ...')
        app = web.Application()
        app.router.add_get('/server/get_sensor_data/{sensor_data}', self.get_sensor_data)
        app.router.add_get('/server/load_service', self.load_service)

        web.run_app(app, host='169.254.12.61', port=8010)


if __name__ == '__main__':
    home_server = HomeServer()
    home_server.main()
