import json
import os
import re
import ast
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
        self.key_to_list_of_primitive_condition = ['con:Context',
                                                   'con:PrimitiveConditionList',
                                                   'con:PrimitiveCondition']
        self.key_to_function_name_in_primitive_condition = ['pc:PrimitiveCondition',
                                                            'pc:Function',
                                                            'pc:FunctionName']

    def current_target_user(self):
        return self.target_user_list[self.current_user]

    def set_current_user(self, user_id):
        self.current_user = user_id

    def load_service_data(self):
        target_user = self.current_target_user()
        with open(self.path_to_cwd + '/' + f'user/{target_user}/service/concrete'
                                           f'/service/Concrete_Service_{target_user}.json',
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

    def get_serial_number_in_service(self):
        device_list = get_data_of_specified_key(self.load_service_data(),
                                                self.key_to_device_list_in_service)
        serial_number_in_service = device_list
        serial_number_in_service = \
            get_data_of_specified_key(serial_number_in_service,
                                      self.key_to_serial_number_in_service)

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
                                      self.key_to_list_of_primitive_condition)

        return list_of_primitive_condition

    def compare_device_name_with_device_name(self):
        target_data = \
            matched_data_from_the_key_above_and_below(self.get_serial_number_in_service(),
                                                      self.load_device_information(),
                                                      self.key_to_device_list_in_device_information,
                                                      ['dev:SerialNumber'],
                                                      ['dev:DeviceName'])
        # print('single test')
        check_data = matched_data_from_the_key_above_and_below(target_data,
                                                               self.load_context(),
                                                               self.key_to_list_of_primitive_condition,
                                                               ['con:DeviceName', '#text'],
                                                               ['@uri'])
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
        # self.load_primitive_condition(self.path_to_cwd, dict_of_primitive_condition)

    def load_primitive_condition(self):
        path_to_primitive_condition: object = self.compare_device_name_with_device_name()
        url = remove_localhost(path_to_primitive_condition)
        file_name = remove_localhost(path_to_primitive_condition)
        file_name = file_name.split('/')
        file_name = file_name[3:]
        file_name = ''.join(file_name)
        # print(file_name)
        with open(self.path_to_cwd + url + '/'
                  + file_name + '.json', mode='r',
                  encoding='utf-8') as primitive_condition:
            primitive_condition_data = json.load(primitive_condition)
        # print(f'primitive_condition_data: {primitive_condition_data}')
        return primitive_condition_data

    def pack_primitive_condition(self, arg1, arg2):
        primitive_condition_data = self.load_primitive_condition()
        right = primitive_condition_data[arg1][arg2]
        # print(right)
        primitive_condition_dict = f"'{arg2}'" + ': ' + str(right)
        # print(primitive_condition_dict)
        return primitive_condition_dict

    def service_primitive_pack(self):
        primitive_condition_equation = str(self.dict_of_primitive_condition_equation())
        condition_value = get_data_of_specified_key(self.load_service_data(),
                                                    self.key_to_device_list_in_service)
        value_list = str(condition_value['ns2:Device']['ns2:Value'])
        serial_number = str(condition_value['ns2:Device']['ns2:SerialNumber'])
        pack2 = self.pack_primitive_condition('pc:PrimitiveCondition', 'pc:Function')
        pack3 = self.pack_primitive_condition('pc:PrimitiveCondition', 'pc:Value')
        packed_dict = '{' + "'ns2:SerialNumber': "+ "'" + serial_number + "'" \
                      + ', ' + pack2 + ', ' + pack3 \
                      + ", 'ns2:Value': " + value_list + '}'
        # print(packed_dict)
        return packed_dict

    def eval_id_primitive_dict(self):
        conditional_equation_dict = self.service_primitive_pack()
        # print(type(conditional_equation_dict))
        eval_dict = ast.literal_eval(conditional_equation_dict)
        return eval_dict

    def join_packed_condition(self):
        # condition_value = get_data_of_specified_key(self.load_service_data(),
        #                                            self.key_to_device_list_in_service)
        # condition_value = str(condition_value['ns2:Device']['ns2:Value'])
        # print(device_id_in_service)
        # print(condition_value)
        condition_dict = (self.eval_id_primitive_dict())
        # print(condition_dict)
        condition_dict = str(condition_dict)
        join_data = '{' + "'" + 'packed_condition' + "'" + ': ' + condition_dict + '}'
        # print(join_data)
        join_data = ast.literal_eval(join_data)
        # pprint(type(join_data))
        print('matched condiiton is ...')
        return join_data

    def call_logical_expression(self):
        self.set_current_user(2)
        logical_expression = "{" "'ConditionEquation': " + f"'{self.simple_condition_equation()}'" + "}"
        return logical_expression

    def call_condition_equation(self):
        self.set_current_user(2)
        concrete_condition_equation = self.search_matched_device_name_with_serial()
        return concrete_condition_equation

    def get_serial_number(self):
        serial_number = get_data_of_specified_key(self.load_service_data(),
                                                      self.key_to_serial_number_in_service)
        return serial_number

    def get_device_list(self):
        device_list = get_data_of_specified_key(self.load_device_information(),
                                                self.key_to_device_list_in_device_information)
        return device_list

    def search_matched_device_name_with_serial(self):
        condition_equationdict = {}
        use_serial_number = self.get_serial_number_in_service()
        device_list = self.get_device_list()
        for device in device_list:
            if device['dev:SerialNumber'] == use_serial_number:
                device_name = device['dev:DeviceName']
                condition_equationdict.update(self.search_id_of_primitive_condition(device_name))
        return condition_equationdict

    def search_id_of_primitive_condition(self, device_name):
        primitive_condition_list = get_data_of_specified_key(self.load_context(),
                                                             self.key_to_list_of_primitive_condition)
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
                                   + "'FunctionName': "  + f"'{self.find_function_name()}'," \
                                   + "'Value': "         + f"'{value}'" + "}"
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

    def call_packed_condition(self, num):
        self.set_current_user(num)
        return self.join_packed_condition()

    def main(self):
        # User(A-C:0~2)
        print(self.call_logical_expression())
        print(self.call_condition_equation())
        # print(self.primitive_condition_equation())
        # print(self.join_packed_condition())


if __name__ == '__main__':
    matcon = MatchContext()
    matcon.main()
