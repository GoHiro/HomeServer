import json
import os
import re
import ast
import datetime
from pprint import pprint


def remove_localhost(path: object) -> str:
    return path.replace("http://localhost:8000/", "/", 1)


def get_data_of_specified_key(target_data: dict, key_to_target_data: list):
    for key in key_to_target_data:
        target_data = target_data[key]

    return target_data


def matched_data_from_the_key_above_and_below(target_data,
                                              search_data, key_to_above,
                                              key_to_below, key_to_next_value):
    global next_value, matched_data
    above_value = \
        get_data_of_specified_key(search_data,
                                  key_to_above)

    for i in range(len(above_value)):
        list_value = above_value[i]
        # print(f'aboveiiiiiiii: {list_value}')
        for key in key_to_below:
            if key == key_to_below[len(key_to_below) - 1]:
                for next_key in key_to_next_value:
                    next_value = list_value[next_key]

                    # print(f'next_value: {next_value}')
            # print(f'above_value: {list_value}')
            # print(f'key_below: {key_below}')
            list_value = list_value[key]

        if list_value == target_data:
            # print('target_data confirmed')
            matched_data = next_value
            break
        else:
            print('target_data not found')
            matche_data = None
            # print(f'above_value: {list_value}')
            # print(f'target_data: {target_data}')

    return matched_data


class MatchContext:
    def __init__(self):
        """
        path_to = @uri
        key_to = json_key
        """

        self.target_user_list = ['A', 'B', 'C']
        self.path_to_cwd = os.getcwd()  # cwd = current working directory
        self.key_to_serial_number_in_service = ['ns2:Device', 'ns2:SerialNumber']
        self.key_to_function_name_in_service = ['ns2:Device', 'ns2:Function',
                                                'ns2:FunctionName']
        self.path_to_device_information = '/HNS/DeviceInformation/'
        self.key_to_device_list_in_service = ['ConcreteService', 'ConditionOperationSetList',
                                              'ConditionOperationSet', 'ns2:Condition',
                                              'ns2:ContextGroupList', 'ns2:ContextGroup',
                                              'ns2:ContextList', 'ns2:Context', 'ns2:DeviceList']
        self.key_to_device_list_in_device_information = ['dev:DeviceInformation',
                                                         'dev:DeviceList',
                                                         'dev:Device']
        self.key_to_primitive_condition_list = ['con:Context',
                                                'con:PrimitiveConditionList',
                                                'con:PrimitiveCondition']
        self.key_to_function_name_in_primitive_condition = ['pc:PrimitiveCondition',
                                                            'pc:Function',
                                                            'pc:FunctionName']
        self.key_to_sequence_list_in_service = ['ConcreteService', 'ConditionOperationSetList',
                                                'ConditionOperationSet', 'ns3:Operation',
                                                'ns3:AbstractOperationGroupList', 'ns3:AbstractOperationGroup',
                                                'ns3:AbstractOperationList', 'ns3:AbstractOperation',
                                                'ns3:DeviceList', 'ns3:Device']

    def current_target_user(self):
        return self.target_user_list[self.current_user]

    def set_current_user(self, user_id):
        self.current_user = user_id

    def set_current_service_name(self, service_name):
        self.current_name = service_name

    def load_service_data(self):
        target_user = self.current_target_user()
        target_name = self.current_name
        with open(self.path_to_cwd + '/' + f'user/{target_user}/service/concrete'
                                           f'/service/{target_name}.json',
                  mode='r', encoding='utf-8') as service:
            service_data = json.load(service)
            return service_data

    def search_path_to_context(self):
        key_to_context = ['ConcreteService', 'ConditionOperationSetList',
                          'ConditionOperationSet', 'ns2:Condition',
                          'ns2:ContextGroupList', 'ns2:ContextGroup',
                          'ns2:ContextList', 'ns2:Context', '@uri']
        path_to_context = get_data_of_specified_key(self.load_service_data(),
                                                    key_to_context)
        path_to_context = remove_localhost(path_to_context)

        return path_to_context

    def load_context(self):
        path_to_context = self.search_path_to_context()
        path_to_context = str(path_to_context)
        with open(self.path_to_cwd + path_to_context + '.json', mode='r',
                  encoding='utf-8') as context:
            context_data = json.load(context)

        return context_data

    def primitive_condition_equation(self):
        key_to_primitive_condition_equation = ['con:Context',
                                               'con:PrimitiveConditionEquationList',
                                               'con:PrimitiveConditionEquation']
        primitive_condition_equation = get_data_of_specified_key(self.load_context(),
                                                                 key_to_primitive_condition_equation)

        # print(f'conditional_equation: {conditional_equation}')

        return primitive_condition_equation

    def dict_of_primitive_condition_equation(self):
        key_to_list_of_primitive_condition_equation = ['con:Context',
                                                       'con:PrimitiveConditionEquationList']
        dict_of_primitive_condition_equation = get_data_of_specified_key(self.load_context(),
                                                                         key_to_list_of_primitive_condition_equation)

        return_dict = "'" + 'con:PrimitiveConditionEquationList' + "'" \
                      + ': ' + str(dict_of_primitive_condition_equation)
        # print(f'conditional_equation: {conditional_equation}')

        return return_dict

    def simple_condition_equation(self):
        key_to_list_of_primitive_condition_equation = ['con:Context',
                                                       'con:PrimitiveConditionEquationList']
        simple_condition_equation = get_data_of_specified_key(self.load_context(),
                                                              key_to_list_of_primitive_condition_equation)
        simple_condition_equation = simple_condition_equation['con:PrimitiveConditionEquation']
        return simple_condition_equation

    def load_device_information(self):
        target_user = self.current_target_user()
        with open(self.path_to_cwd + self.path_to_device_information
                  + f'{target_user}.json',
                  mode='r', encoding='utf-8') as device_information:
            device_information = json.load(device_information)

        return device_information

    def get_serial_number_in_service(self, dict_count):
        device_list = get_data_of_specified_key(self.load_service_data(),
                                                self.key_to_device_list_in_service)
        serial_number_in_service = device_list["ns2:Device"][dict_count]["ns2:SerialNumber"]
        pprint(device_list)
        print(serial_number_in_service)
        return serial_number_in_service

    def get_function_name_in_service(self):
        device_list_in_service = get_data_of_specified_key(self.load_service_data(),
                                                           self.key_to_device_list_in_service)
        function_name_in_service = device_list_in_service
        function_name_in_service = \
            get_data_of_specified_key(function_name_in_service,
                                      self.key_to_function_name_in_service)

        return function_name_in_service

    # def search_device_list_in_device_information(self):
    #    list_of_primitive_condition = self.search_list_of_primitive_condition()
    #    print(list_of_primitive_condition)

    def search_list_of_primitive_condition(self):
        context_data = self.load_context()
        list_of_primitive_condition = \
            get_data_of_specified_key(context_data,
                                      self.key_to_primitive_condition_list)

        return list_of_primitive_condition

    def compare_device_name_with_device_name(self):
        # todo
        while (True):
            dict_count = 0
            print(dict_count)
            target_data = matched_data_from_the_key_above_and_below(self.get_serial_number_in_service(dict_count),
                                                                    self.load_device_information(),
                                                                    self.key_to_device_list_in_device_information,
                                                                    ['dev:SerialNumber'],
                                                                    ['dev:DeviceName'])
            print(f'target_data: {target_data}')
            if target_data is not None:
                break
            elif target_data is None:
                dict_count += 1
        check_data = matched_data_from_the_key_above_and_below(target_data,
                                                               self.load_context(),
                                                               self.key_to_primitive_condition_list,
                                                               ['con:DeviceName', '#text'],
                                                               ['@uri'])
        print(f'check_data: {check_data}')
        return check_data

    def primitive_condition_device_name(self):
        # compare_#text_with_next_value
        dict_of_primitive_condition = self.search_list_of_primitive_condition()
        primitive_condition_device_name = dict_of_primitive_condition['#text']
        primitive_condition_device_name = \
            (re.sub('\n', '', primitive_condition_device_name))
        primitive_condition_device_name = \
            (re.sub(' *', '', primitive_condition_device_name))
        print(f'primitive_condition_device_name: {primitive_condition_device_name}')

    def path_to_primitive_condition(self):
        dict_of_primitive_condition = self.search_list_of_primitive_condition()
        dict_of_primitive_condition = dict_of_primitive_condition['@uri']
        dict_of_primitive_condition = remove_localhost(dict_of_primitive_condition)
        print(f'path_to_primitive_condition: {dict_of_primitive_condition}')

    def format_file_name(self, file_name):
        file_name = file_name.split('/')
        file_name = file_name[3:]
        file_name = ''.join(file_name)
        return file_name

    def load_primitive_condition(self):
        path_to_primitive_condition = self.compare_device_name_with_device_name()
        url = remove_localhost(path_to_primitive_condition)
        file_name = remove_localhost(path_to_primitive_condition)
        file_name = self.format_file_name(file_name)
        with open(self.path_to_cwd + url + '/'
                  + file_name + '.json', mode='r',
                  encoding='utf-8') as primitive_condition:
            primitive_condition_data = json.load(primitive_condition)
        return primitive_condition_data

    def pack_primitive_condition(self, arg1, arg2):
        primitive_condition_data = self.load_primitive_condition()
        right = primitive_condition_data[arg1][arg2]
        primitive_condition_dict = f"'{arg2}'" + ': ' + str(right)
        return primitive_condition_dict

    def service_primitive_pack(self):
        packed_condition_list = []
        primitive_condition_equation = str(self.dict_of_primitive_condition_equation())
        condition_value = get_data_of_specified_key(self.load_service_data(),
                                                    self.key_to_device_list_in_service)
        for condition in condition_value["ns2:Device"]:
            packed_condition_list.append(self.insert_condition_value(condition))
        return packed_condition_list

    def insert_condition_value(self, condition):
        value_list = str(condition['ns2:Value'])
        serial_number = str(condition['ns2:SerialNumber'])
        # fixme: find primitive_condition from serial_number
        dev_device_name = self.find_device_name_by_serial_number(serial_number)
        primitive_condition_uri = self.find_primitive_condition_uri_by_device_name(dev_device_name)
        primitive_condition = self.load_primitive_condition_by_uri(primitive_condition_uri)
        function_name = primitive_condition["pc:PrimitiveCondition"]["pc:Function"]["pc:FunctionName"]
        pc_value = primitive_condition["pc:PrimitiveCondition"]["pc:Value"]
        packed_dict = '{' + "'ns2:SerialNumber': " + "'" + serial_number + "'" + ', ' \
                      + "'pc:FunctionName': " + "'" + str(function_name) + "'" + ', ' \
                      + "'pc:Value': " + str(pc_value) + ',' \
                      + "'ns2:Value': " + value_list + '}'
        print('packed_dict')
        print(packed_dict)
        packed_dict = ast.literal_eval(packed_dict)
        return packed_dict

    def load_primitive_condition_by_uri(self, primitive_condition_uri):
        uri = remove_localhost(primitive_condition_uri)
        file_name = remove_localhost(primitive_condition_uri)
        file_name = self.format_file_name(file_name)
        with open(self.path_to_cwd + uri + '/' + file_name + '.json',
                  mode='r', encoding='utf-8') as pcon:
            primitive_condition = json.load(pcon)
        return primitive_condition

    def find_device_name_by_serial_number(self, serial_number):
        dev_device_list = self.get_dev_device_list()
        for list in dev_device_list:
            if list["dev:SerialNumber"] == serial_number:
                dev_device_name = list["dev:DeviceName"]
                break
        return dev_device_name

    def get_dev_device_list(self):
        return get_data_of_specified_key(self.load_device_information(), self.key_to_device_list_in_device_information)

    def find_primitive_condition_uri_by_device_name(self, device_name):
        primitive_condition_list = get_data_of_specified_key(self.load_context(),
                                                             self.key_to_primitive_condition_list)
        for list in primitive_condition_list:
            if list["con:DeviceName"]["#text"] == device_name:
                primitive_condition_uri = list["con:DeviceName"]["@uri"]
                break
        return primitive_condition_uri

    def eval_id_primitive_dict(self):
        eval_dict = self.service_primitive_pack()
        return eval_dict

    def join_packed_condition(self):
        condition_dict = (self.eval_id_primitive_dict())
        condition_dict = str(condition_dict)
        join_data = '{' + "'" + 'packed_condition' + "'" + ': ' + condition_dict + '}'
        join_data = ast.literal_eval(join_data)
        print('matched condiitons to register ...')
        return join_data

    def call_logical_expression(self, service_id, service_name):
        self.set_current_user(service_id)
        self.set_current_service_name(service_name)
        logical_expression = "{" "'ConditionEquation': " + f"'{self.simple_condition_equation()}'" + "}"
        return logical_expression

    def call_condition_equation(self, service_id, service_name):
        """{"id1": {primitive_condition1},
            "id2": {primitive_condition2}, ...}"""
        self.set_current_user(service_id)
        self.set_current_service_name(service_name)
        concrete_condition_equation = {}
        # concrete_condition_equation = self.search_matched_device_name_with_serial()
        condition_value = get_data_of_specified_key(self.load_service_data(), self.key_to_device_list_in_service)
        for condition in condition_value["ns2:Device"]:
            del condition['@id']
            serial_number = condition['ns2:SerialNumber']
            device_name = self.find_device_name_from_serial_number(serial_number)
            primitive_condition_id = self.find_primitive_condition_id_from_device_name(device_name)
            # fixme: condition -> translated_condition
            translated_condition = self.condition_contain_translated_value(serial_number,function_name=condition['ns2:Function']['ns2:FunctionName'],value_dict=condition['ns2:Value'])
            part_of_concrete_condition_equation = {primitive_condition_id: translated_condition}
            concrete_condition_equation.update(part_of_concrete_condition_equation)
        print('concrete_condition_equation')
        print(concrete_condition_equation)
        return concrete_condition_equation

    def condition_contain_translated_value(self, serial_number, function_name, value_dict):
        translated_value = self.translate_to_value(value_dict)
        condition_frame = {'SerialNumber': serial_number,'FunctionName': function_name, 'Value': translated_value}
        return condition_frame

    def find_device_name_from_serial_number(self, serial_number):
        device_list = self.get_device_list()
        print(device_list)
        for device in device_list:
            if device['dev:SerialNumber'] == serial_number:
                name = device['dev:DeviceName']
        print(name)
        return name

    def find_primitive_condition_id_from_device_name(self, device_name):
        primitive_condition_list = get_data_of_specified_key(self.load_context(), self.key_to_primitive_condition_list)
        id = [primitive_condition['@id'] for primitive_condition in primitive_condition_list if
              primitive_condition['con:DeviceName']['#text'] == device_name]
        print(id)
        return id[0]

    def get_serial_number(self):
        serial_number = get_data_of_specified_key(self.load_service_data(),self.key_to_serial_number_in_service)
        return serial_number

    def get_device_list(self):
        device_list = get_data_of_specified_key(self.load_device_information(),self.key_to_device_list_in_device_information)
        return device_list

    def search_matched_device_name_with_serial(self):
        # fixme: cant use ,need fix
        condition_equationdict = {}
        device_list = self.get_device_list()
        use_serial_number = self.get_serial_number_in_service()

        for device in device_list:
            if device['dev:SerialNumber'] == use_serial_number:
                device_name = device['dev:DeviceName']
                condition_equationdict.update(self.search_id_of_primitive_condition(device_name))
        return condition_equationdict

    def search_id_of_primitive_condition(self, device_name):
        primitive_condition_list = get_data_of_specified_key(self.load_context(),
                                                             self.key_to_primitive_condition_list)
        for primitive_condition in primitive_condition_list:
            if primitive_condition['con:DeviceName']['#text'] == device_name:
                primitive_condition_id = primitive_condition['@id']
                concrete_condition_equation = self.create_condition_equation(str(primitive_condition_id))
        return concrete_condition_equation

    def create_condition_equation(self, primitive_condition_id):
        condition_equation = "{" + "'id" + f"{primitive_condition_id}" + "': " \
                             + f"{self.part_of_condition_equation()}" + "}"
        condition_equation = ast.literal_eval(condition_equation)
        return condition_equation

    def part_of_condition_equation(self):
        concrete_value = get_data_of_specified_key(self.load_service_data(), self.key_to_device_list_in_service)
        value = self.translate_to_value(concrete_value['ns2:Device']['ns2:Value'])
        serial_number = str(concrete_value['ns2:Device']['ns2:SerialNumber'])
        part_of_condition_equation = "{'SerialNumber': " + f"'{serial_number}'," \
                                     + "'FunctionName': " + f"'{self.find_function_name()}'," \
                                     + "'Value': " + f"'{value}'" + "}"
        return part_of_condition_equation

    def translate_to_value(self, value_dict):
        value_type = value_dict['@type']
        value_type = self.judge_value_type(value_type)
        value_text = value_dict['#text']
        value_text = self.judge_value_text(value_text)
        translate_value = value_type + value_text  # ==True
        return translate_value

    def judge_value_type(self, value_type):
        if value_type == 'equal':
            judged_type = '=='
        elif value_type == 'upper':
            judged_type = '>='
        elif value_type == 'lower':
            judged_type = '<'
        else:
            print('no matched type')
            judged_type = 0
        return judged_type

    def judge_value_text(self, value_text):
        if value_text == 'TRUE':
            judged_value = 'True'
        elif value_text == 'FALSE':
            judged_value = 'False'
        else:
            judged_value = value_text
        return judged_value

    def find_function_name(self):
        function_name = get_data_of_specified_key(self.load_primitive_condition(),
                                                  self.key_to_function_name_in_primitive_condition)
        return function_name

    def call_packed_condition(self, service_id, service_name):
        self.set_current_user(service_id)
        self.set_current_service_name(service_name)
        return self.join_packed_condition()

    def call_sequence_list(self, service_id, service_name):
        self.set_current_user(service_id)
        self.set_current_service_name(service_name)
        sequence_of_behavior = get_data_of_specified_key(self.load_service_data(),
                                                         self.key_to_sequence_list_in_service)
        print(sequence_of_behavior)
        return sequence_of_behavior

    def call_device_name_pared_serial_number(self, service_id, current_serial_number):
        self.set_current_user(service_id)
        device_list = get_data_of_specified_key(self.load_device_information(),
                                                self.key_to_device_list_in_device_information)
        for device in device_list:
            if device['dev:SerialNumber'] == current_serial_number:
                return device['dev:DeviceName']

    def call_priority_list(self, service_id, target_service_name_list):
        priority_list = []
        key_to_priority = ['ConcreteService', 'Priority']
        self.set_current_user(service_id)
        for service_name in target_service_name_list:
            self.set_current_service_name(service_name)
            priority_list.append(int(get_data_of_specified_key(self.load_service_data(),
                                                           key_to_priority)))
        return priority_list

    def call_time_condition_list(self, service_id, service_name):
        self.set_current_user(service_id)
        self.set_current_service_name(service_name)
        key_to_time_condition = ['ConcreteService', 'ConditionOperationSetList',
                                 'ConditionOperationSet', 'ns2:Condition', 'ns2:TimeCondition', 'ns2:Value']
        time_condition = get_data_of_specified_key(self.load_service_data(),
                                                   key_to_time_condition)
        return time_condition

    def call_check_service_has_after_condition(self,service_id, service_name):
        self.set_current_user(service_id)
        self.set_current_service_name(service_name)
        key_to_after_condition = ['ConcreteService', 'ConditionOperationSetList',
                                  'ConditionOperationSet']
        after_condition = get_data_of_specified_key(self.load_service_data(),
                                                    key_to_after_condition)
        if after_condition.get('ns4:AfterCondition'):
            return True
        else:
            return False

    def call_load_after_condition(self,service_id, service_name):
        self.set_current_user(service_id)
        self.set_current_service_name(service_name)
        key_to_after_condition = ['ConcreteService', 'ConditionOperationSetList',
                                 'ConditionOperationSet', 'ns4:AfterCondition']
        after_condition = get_data_of_specified_key(self.load_service_data(),
                                                    key_to_after_condition)
        after_condition['ServiceName'] = service_name
        return after_condition

    def call_device_information_with_id(self, service_id):
        self.set_current_user(service_id)
        device_information = self.load_device_information()
        return device_information

    def call_purpose_and_priority(self, service_id, service_name):
        self.set_current_user(service_id)
        self.set_current_service_name(service_name)
        key_to_purpose_priority = ['ConcreteService']
        purpose_and_priority_dict = get_data_of_specified_key(self.load_service_data(),
                                                              key_to_purpose_priority)
        return purpose_and_priority_dict

    def main(self):
        self.set_current_user(2)  # User_list(A-C:0~2)
        print(self.call_logical_expression())
        print(self.call_condition_equation())


if __name__ == '__main__':
    matcon = MatchContext()
    matcon.main()
