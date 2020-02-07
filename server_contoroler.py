import asyncio


class ServerController:
    def __init__(self):
        self.sequence_list = [{'@seq': '1', 'ns3:SerialNumber': 'Fan C', 'ns3:FunctionList':
            {'ns3:Function': [
                {'@seq': '1', 'ns3:FunctionName': 'OperatingStatus', 'ns3:Value': 'ON'},
                {'@seq': '2', 'ns3:FunctionName': 'TemperatureSettingValue', 'ns3:Value': '33'},
                {'@seq': '3', 'ns3:FunctionName': 'FanSpeed', 'ns3:Value': '4'}]}}]


    async def http_client(self, host, port, msg, loop):
        reader, writer = await asyncio.open_connection(
            host, port, loop=loop
        )

        writer.write(msg.encode())
        data = await reader.read()
        print(f'Received: {data.decode()}')
        writer.close()

    def load_service(self):
        print('サーバへサービスの読み込みをリクエストします')
        host = '169.254.12.61'
        port = 8010
        msg = (
            f'GET /server/load_service HTTP/1.1\r\n'
            'Host: localhost:8010\r\n'
            '\r\n'
            '\r\n'
        )

        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.http_client(host, port, msg, loop))
        loop.close()


    def main(self):
        self.load_service()


if __name__ == '__main__':
    server_c = ServerController()
    server_c.main()
