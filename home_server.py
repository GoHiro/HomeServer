from aiohttp import web
import asyncio
import json
import serial
from struct import *
from binascii import *
import ast
import time
import match_context
# matcon = match_context.MatchContext()

async def get_data_of_specified_key(target_data: object, key_to_target_data: object) -> object:
    for key in key_to_target_data:
        target_data = target_data[key]
    return target_data

async def replace_reserved_strings(res_str):
    reserved_to_unreserved = {'{': 'above_curly', ':': 'middle_colon',
                              '}': 'below_curly', "'": 'top_quote', ',': 'under_comma',
                              '@': 'attribute_at', '#': 'text_sharp', ' ': 'margin_space'}
    for reserved, unreserved in reserved_to_unreserved.items():
        res_str = res_str.replace(f'{reserved}', f'{unreserved}')
    return res_str

async def replace_previous_string(res_str):
    # original string replaces to usable string on arrangement of http
    unreserved_to_previous_string = {'above_curly': '{', 'middle_colon': ':',
                                     'below_curly': '}', 'top_quote': "'", 'under_comma': ',',
                                     'attribute_at': '@', 'text_sharp': '#', 'margin_space': ' '}
    for unreserved, previous in unreserved_to_previous_string.items():
        res_str = res_str.replace(f'{unreserved}', f'{previous}')
    return res_str


class OperatingDevice:
    def __init__(self):
        self.function_serial_dict = {'IRLightStatusON': 'ffff0000'}
        # current_device_state will change that load from 'current_device_state.json'
        self.current_device_state = {'Fan C':{'OperatingStatus': 'OFF',
                                              'TemperatureSettingValue': '37',
                                              'FanSpeed': '5'}}

    async def call_service_behavior(self, service_id):
        await self.get_device_name(service_id)

    async def get_function_serial_of_current_serial_number(self, function_name):
        checked_dict = self.function_serial_dict
        serial_key = [self.serial_number_in_current_sequence, function_name]
        serial_of_function = [checked_dict[key] for key in serial_key]
        return serial_of_function

    async def get_device_name(self, service_id):
        matcon = match_context.MatchContext()
        await matcon.set_current_user(service_id)
        device_list = await get_data_of_specified_key(matcon.load_device_information(),
                                                      matcon.key_to_device_list_in_device_information)
        await self.get_function_list_per_device_sequence(device_list)

    async def get_function_list_per_device_sequence(self, device_list):
        for device_seq in device_list:
            self.serial_number_in_current_sequence = device_seq['ns3:SerialNumber']
            function_list = device_seq['ns3:FunctionList']
            await self.get_function_per_function_sequence(function_list)

    async def get_function_per_function_sequence(self, function_list):
        for func_seq in function_list:
            function_name = func_seq['ns3:FunctionName']
            function_value = func_seq['ns3:Value']
            matcon = match_context.MatchContext()
            if function_value == await self.get_current_function_value(function_name):
                continue
            elif isinstance(function_value, str):
                await self.call_strings_behavior(function_name)
            elif isinstance(function_value, int):
                await self.call_integer_behavior(function_value, function_name)

    async def get_current_function_value(self, function_name):
        key_to_current_function_value = [self.serial_number_in_current_sequence,
                                         function_name]

    async def call_strings_behavior(self, function_name):
        set_serial = await self.get_function_serial_of_current_serial_number(function_name)
        await IRControler.set_serial_of_function(set_serial)
        await IRControler.send_serial_for_appliance()
        await time.sleep(1)

    async def call_integer_behavior(self, function_value, function_name):
        set_serial = await self.get_function_serial_of_current_serial_number(function_name)
        await IRControler.set_serial_of_function(set_serial)
        matcon = match_context.MatchContext()
        send_count = abs(await matcon.get_current_function_value() - function_value)
        while True:
            if send_count <= 0:
                break
            send_count -= 1
            await IRControler.send_serial_for_appliance()
            await time.sleep(1)


class IRControler:
    def __init__(self):
        print('set IRControler stats')

    async def send_serial_for_appliance(self):
        print('set serial send to appliance')

    async def set_serial_of_function(self, set_serial):
        print('Set serial for sending appliance')


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

        self.enviroment_field = {}

        self.kaden = 0
        self.state = 0
        self.channel = 0
        self.temp = 0
        self.rtemp = 0
        self.vol = 0
        self.time = 0
        self.settei = 0
        self.dict = {}

        # csv
        # self.f = open('data.csv', 'r')
        # self.reader = csv.reader(self.f)
        # for row in self.reader:
        #    self.l_value = [row[1], row[2], row[3]]
        # 学習リモコンの on/off の 値も読み込めるようにする
        #    self.dict.update({row[0]: self.l_value})
        #    print(self.dict)

        self.ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=5)
        self._LED = pack('B', 0x69)  # LED 点灯
        self._RECEIVE = pack('B', 0x72)  # 受信
        self._TRANSMIT = pack('B', 0x74)  # 送信
        self.ch1 = pack('B', 0x31)  # A (黄)
        self.ch2 = pack('B', 0x32)  # A (黒)
        self.ch3 = pack('B', 0x33)  # B (黄)
        self.ch4 = pack('B', 0x34)  # B (黒)
        self.r_data = 0  # 受信する際の変数

    def diction(self, value):
        # self.dict['value']を出力
        print(self.dict[str(value)])

        # change_name実行(引数:dict['value'][0])
        # self.change_name(self.dict[str(value)][0])

        # change_state実行(引数:dict['value'][1])
        # self.change_state(self.dict[str(value)][1])

        # 学習リモコンに送る信号命令を出力、送信
        print(self.ch1)
        print(self.dict[str(value)][2])
        self.transmit(self.dict[str(value)][2], self.ch1)

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
        """ 赤外線を送信する"""

        bin_data = a2b_hex(hex_data)
        self.ser.write(self._TRANSMIT)
        self.ser.read(1)  # 0x59
        self.ser.write(channel)  # チャンネルの指定
        self.ser.read(1)  # 0x59
        self.ser.write(bin_data)  # データの送信
        self.ser.read(1)  # 0x45

    def __enter__(self):
        return self

    # サービス.jsonをdumpのあと、with openしたサービス.jsonをcloseする
    def __exit__(self, *args):
        print('self.ser.close()実行')
        self.ser.close()

    # Streams: sending and receiving data without using callbacks
    async def http_client(self, host, port, msg, loop):
        reader, writer = await asyncio.open_connection(
            host, port, loop=loop
        )

        writer.write(msg.encode())
        data = await reader.read()
        print(f'Received: {data.decode()}')
        writer.close()

    # サービス.jsonを読み込み、値をlist型の'data'に格納
    async def load_service(self, request):
        print('サービスを読み込み、条件の値を読み込む')
        with open('service.json', mode='r', encoding='utf-8') as f:
            data = json.load(f)

            self.service.append(data['service_name'])
            self.smart_sensor_port = int(data['device_list'][0]['port'])
            self.smart_sensor_condition = int(data['device_list'][0]['condition'])
            self.smart_appliance_port = int(data['device_list'][1]['port'])
            self.smart_appliance_power = data['device_list'][1]['state']
            print(self.service)
            print("smart_sensor_condition = " + str(self.smart_sensor_condition))
            print("smart_appliance_state = " + self.smart_appliance_power)
            self.smart_appliance_name = data['device_list'][1]['device_name']
            print(self.smart_appliance_name)
            self.smart_appliance_send_param = data['device_list'][1]['send_param']
            print(self.smart_appliance_send_param)
            self.smart_appliance_mode = data['device_list'][1]['send_param']
            print(self.smart_appliance_mode)

            # 学習リモコンの on/off の 値を読み込む
            self.l_value = [self.smart_appliance_name, self.smart_appliance_mode, self.smart_appliance_send_param]
            self.dict.update({self.smart_appliance_power: self.l_value})
            print('dict:' + str(self.dict))

            await self.set_condition()

    async def set_service_value(self):

        await self.set_condition()

    async def set_condition(self):
        print('センサーへ条件の登録を行います')
        host = '169.254.137.173'
        port = self.smart_sensor_port
        matcon = match_context.MatchContext()
        condition_dict = matcon.call_packed_condition(2)
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

    # request内部の式'sensor_data'から受信データを取り出す
    async def get_sensor_data(self, request):
        get_data = request.match_info.get('sensor_data', "Anonymous")
        get_data = await replace_previous_string(get_data)
        get_data = ast.literal_eval(get_data)

        # please make a field of enviroment
        await self.store_enviroment_field(get_data)
        await self.compare_enviroment_field_with_condition_equation()
        # await self.check_service_condition()
        return web.Response(text='ok')
        # self.smart_sensor_condition == self.received_data
        # or
        # context_list.con:PrimitiveConditionEquation == device_list.current_enviroment

    async def store_enviroment_field(self, get_data):
        serial_number = get_data['SerialNumber']
        function_name = get_data['FunctionName']
        value = get_data['Value']
        if self.enviroment_field.get(str(serial_number)) not in self.enviroment_field:
            temp_dict = {function_name: value}
            self.enviroment_field[serial_number] = temp_dict
            print(self.enviroment_field)
        elif self.enviroment_field[serial_number].get(function_name) not in self.enviroment_field:
            self.enviroment_field[serial_number][function_name] = value
            print(self.enviroment_field)

    async def call_logical_expression(self):
        matcon = match_context.MatchContext()
        self.logical_expression = matcon.call_logical_expression()
        self.logical_expression = ast.literal_eval(self.logical_expression)
        print(self.logical_expression)

    async def call_condition_equation(self):
        matcon = match_context.MatchContext()
        self.condition_equation = matcon.call_condition_equation()

        print(self.condition_equation)

    async def compare_enviroment_field_with_condition_equation(self):
        await self.call_logical_expression()
        await self.call_condition_equation()
        check_list = await self.check_true_primitive_condition()
        if await self.check_logical_expression_by_check_list(check_list):
            print(check_list)
            service_id = 2
            await self.service_execute(service_id)

    async def service_execute(self, service_id):
        print(f'Service {service_id} activate...')
        await OperatingDevice.call_service_behavior(service_id)

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
        print(logical_expression)
        return eval(logical_expression)

    async def check_true_primitive_condition(self):
        check_list = [0] * (await self.count_string_of_logical_expression())
        for id in range(await self.count_string_of_logical_expression()):
            if await self.contained_id_primitive_condition(id):
                if await self.check_true_primitive_condition_per_id(id):
                    check_list[id] = '1'
            else:
                check_list[id] = '0'
        print(f'check_list: {check_list}')
        return check_list

    async def contained_id_primitive_condition(self, id):
        logical_expression = str(self.logical_expression)
        if str(id) in logical_expression:
            return True
        else:
            return False

    async def check_true_primitive_condition_per_id(self, id):
        primitive_condition_per_id = await self.get_primitive_condition_per_id(id)
        serial_number = primitive_condition_per_id['SerialNumber']
        function_name = primitive_condition_per_id['FunctionName']
        enviroment_value = self.enviroment_field[serial_number][function_name]
        expression = enviroment_value + primitive_condition_per_id['Value']
        if eval(expression):
            return True

    async def get_primitive_condition_per_id(self, id):
        condition_equation = self.condition_equation
        primitive_condition_per_id = condition_equation['id' + f'{id}']
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

    """async def check_service_condition(self):
        print('条件:' + str(self.smart_sensor_condition) + '<= データ:' + str(self.get_data))
        if self.smart_sensor_condition <= self.get_data:
            print(float(self.get_data))
            print('条件を満たしました、サービスを実行します')
            await self.appliance_power_switch()
        else:
            print('条件を満たしていません')"""

    # cronで一定時間ごとにサービスの条件を比較する、いらない気がしてきた
    async def cron_check_service_condition(self, request):
        print('条件:' + str(self.smart_sensor_condition) + '<= データ:' + str(self.get_data))
        if self.smart_sensor_condition <= self.get_data:
            print(float(self.get_data))
            print('条件を満たしました、サービスを実行します')
            await self.appliance_power_switch()
        else:
            print('条件を満たしていません')

    # 家電へリクエストを送信する。
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
        await loop.create_task(self.http_client(host, port, msg, loop))
        # loop.run_until_complete(self.http_client(host, port, msg, loop)
        # loop.close()
        return web.Response(text='ok')

    # 受信したmsgの'request'を表示する。
    async def msg_test(self, request):
        msg = 'test'
        print(msg)
        print(request)
        return web.Response(text='ok')

    async def appliance_echo(self):
        kadenname = 'test'
        print('テストメッセージを送信します')


    def main(self):
        print('Starting Home Server ...')
        app = web.Application()
        app.router.add_get('/server/get_sensor_data/{sensor_data}', self.get_sensor_data)
        app.router.add_get('/server/msg_test', self.msg_test)
        app.router.add_get('/server/load_service', self.load_service)
        # app.router.add_get('/server/cron_check_service_condition', self.cron_check_service_condition)
        # 学習リモコン初期化
        self.led()
        # 学習リモコン受信
        # self.receive()
        web.run_app(app, host='169.254.12.61', port=8010)


if __name__ == '__main__':
    home_server = HomeServer()
    home_server.main()
