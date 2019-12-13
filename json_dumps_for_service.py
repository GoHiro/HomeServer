import json
import ast
from pprint import pprint


# >> self.replace_target_asterisk(concrete_service, "*user")
# .replace('*user', 'str(input())')
def replace_target_asterisk(block, key):
    block = str(block)
    if key in ser_sct.replace_index:
        block.replace(key, ser_sct.replace_index[key])
    elif key not in ser_sct.replace_index:
        print(f'input value:{key}')
        replace_text = input()
        block = block.replace(key, str(replace_text))
        ser_sct.replace_index[key] = replace_text
    block = ast.literal_eval(block)
    return block


class ServiceStruct:
    def __init__(self):
        self.user_list = ['A', 'B', 'C']
        self.replace_index = {}

    def struct_service(self):
        header = self.get_header()
        body = self.get_body()
        service = {**header, **body}
        return service

    def get_header(self):
        header = {"?xml": {"@version": "1.0",
                           "@encoding": "UTF-8",
                           "@standalone": "yes"}}
        return header

    def get_body(self):
        body = {"ConcreteService": "**concrete_service"}
        body["ConcreteService"] = self.concatenate_concrete_service()
        return body

    def concatenate_concrete_service(self):
        concrete_service = {"@uri": "/user/C/service/concrete/service/*service_name",
                            "@xmlns:ns2": "http://www.example.org/HNS/Service/ConcreteService/ConcreteCondition ",
                            "@xmlns": "http://www.example.org/HNS/Service/ConcreteService/ConcreteService ",
                            "@xmlns:ns4": "http://www.example.org/HNS/Service/ConcreteService/ConcreteAfterCondition ",
                            "@xmlns:ns3": "http://www.example.org/HNS/Service/ConcreteService/ConcreteOperation",
                            "CreatedDate": "2019-10-23T16:21:27.237+09:00",
                            "Summary": "*summary",
                            "AbstractServiceReference":
                                {"@uri": "http://localhost:8080/service/abstractservice/00000001"},
                            "User": "*user",
                            "Name": "*service_name",
                            "ConditionOperationSetList": "**condition_operation_set_list"}
        concrete_service = replace_target_asterisk(block=concrete_service, key="*service_name")
        concrete_service = replace_target_asterisk(block=concrete_service, key="*summary")
        concrete_service = replace_target_asterisk(block=concrete_service, key="user")
        concrete_service = replace_target_asterisk(block=concrete_service, key="*service_name")
        concrete_service["ConditionOperationSetList"] = self.concatenate_condition_operation_set()
        return concrete_service

    def concatenate_condition_operation_set(self):
        condition_operation_set = {"ConditionOperationSet": "**condition_operation"}
        condition_operation_set["ConditionOperationSet"] = self.concatenate_condition_operation()
        return condition_operation_set

    def concatenate_condition_operation(self):
        condition_operation = {"ns2:Condition": "**condition",
                               "ns3:Operation": "**operation",
                               "ns4:AfterCondition": "**after_condition"}
        condition_operation["ns2:Condition"] = self.concatenate_ns2_condition()
        condition_operation["ns3:Operation"] = self.concatenate_ns3_operation()
        condition_operation["ns4:AfterCondition"] = self.concatenate_ns4_after_condition()
        return condition_operation

    def concatenate_ns2_condition(self):
        condition = {"ns2:ConditionEquationList": "**ns2_condition_equation",
                     "ns2:ContextGroupList": "**ns2_context_group"}
        condition["ns2:ConditionEquationList"] = self.concatenate_ns2_condition_equation()
        condition["ns2:ConditionEquationList"] = self.concatenate_ns2_context_group()
        return condition

    def concatenate_ns2_condition_equation(self):
        ns2_condition_equation = {"ns2:ConditionEquation": "*context_id"}
        ns2_condition_equation = replace_target_asterisk(block=ns2_condition_equation, key="*context_id")
        return ns2_condition_equation

    def concatenate_ns2_context_group(self):
        ns2_context_group = {"ns2:ContextGroup": "**ns2_context_group_dict"}
        ns2_context_group["ns2:ContextGroup"] = self.concatenate_ns2_context_group_dict()
        return ns2_context_group

    def concatenate_ns2_context_group_dict(self):
        ns2_context_group_dict = {"@id": "*context_id",
                                  "ns2:ContextEquationList": "**ns2_context_equation",
                                  "ns2:ContextList": "**ns2_context_list"}
        ns2_context_group_dict = replace_target_asterisk(block=ns2_context_group_dict, key="*context_id")
        ns2_context_group_dict["ns2:ContextEquationList"] = self.concatenate_ns2_context_equation()
        ns2_context_group_dict["ns2:ContextList"] = self.concatenate_ns2_context_list()
        return ns2_context_group_dict

    def concatenate_ns2_context_equation(self):
        ns2_context_equation = {"ns2:ContextEquation": "*context_id"}
        ns2_context_equation = replace_target_asterisk(block=ns2_context_equation, key="*context_id")
        return ns2_context_equation

    def concatenate_ns2_context_list(self):
        ns2_context_list = {"ns2:Context": "**context_dict"}
        ns2_context_list["ns2:Context"] = self.concatenate_context_dict()
        return ns2_context_list

    def concatenate_context_dict(self):
        context_dict = {"@id": "*context_id",
                        "@uri": "*context_uri",
                        "ns2:DeviceList": "**ns2_device",
                        "ns2:DeviceConditionEquationList": None}
        context_dict = replace_target_asterisk(block=context_dict, key="*context_id")
        context_dict = replace_target_asterisk(block=context_dict, key="*context_uri")
        context_dict["ns2:DeviceList"] = self.concatenate_ns2_device()
        return context_dict

    def concatenate_ns2_device(self):
        ns2_device = {"ns2:Device": []}
        # todo:recursive append block
        ns2_device = self.recursive_append(block=ns2_device, multi_block=self.append_ns2_device_list(),
                                           key="ns2:Device")
        return ns2_device

    def recursive_append(self, block, multi_block, key):
        recursive_frag = True
        append_frag = True
        while (True):
            print('current block is :')
            pprint(block[key])
            if bool(append_frag):
                # self.multi_append_{mucti_block}
                block[key].append(multi_block)
            append_frag = True
            print('one more? y/n')
            input_key = input()
            if input_key == 'y' or input_key == 'Y':
                print('repeat')
            elif input_key == 'n' or input_key == 'N':
                print('end repeat')
                recursive_frag = False
            else:
                append_frag = False
            if bool(recursive_frag):  # todo
                break

    def append_ns2_device_list(self):
        ns2_device_list = {"@id": "*device_id",
                           "ns2:SerialNumber": "*serial_number",
                           "ns2:Function": "**ns2_function_name",
                           "ns2:Value": "**value_dict"}
        print('*device_id: ')
        ns2_device_list["@id"] = input()
        print('*serial_number: ')
        ns2_device_list["ns2:SerialNumber"] = input()
        ns2_device_list["ns2:Function"] = self.concatenate_ns2_function_name()
        ns2_device_list["ns2:Value"] = self.concatenate_ns2_value_dict()
        return ns2_device_list

    def concatenate_ns2_function_name(self):
        ns2_function_name = {"ns2:FunctionName": "*function_name"}
        print('pls input ns2:FunctionName')
        ns2_function_name["ns2:FunctionName"] = input()
        return ns2_function_name

    def concatenate_ns2_value_dict(self):
        value_dict = {"@type": "*type",
                      "#text": "*text"}
        print('pls input upper/equal/lower: ')
        value_dict["@type"] = input()
        print('pls input numeric/TRUE/FALSE: ')
        value_dict["#text"] = input()
        return value_dict

    def concatenate_ns3_operation(self):
        ns3_operation = {"ns3:AbstractOperationGroupList": "**ns3_abstract_operation_group"}
        ns3_operation["ns3*AbstractOperationGroupList"] = self.concatenate_ns3_abstract_operation_group()
        return ns3_operation

    def concatenate_ns3_abstract_operation_group(self):
        ns3_abstract_operation_group = {"ns3:AbstractOperationGroup": "**ns3_abstract_operation_list"}
        ns3_abstract_operation_group["ns3:AbstractOperationGroup"] = self.concatenate_ns3_abstract_operation_list()
        return ns3_abstract_operation_group

    def concatenate_ns3_abstract_operation_list(self):
        ns3_abstract_operation_list = {"ns3:AbstractOperationList": "**ns3_abstract_operation_list"}
        ns3_abstract_operation_list["ns3:AbstractOperationList"] = self.concatenate_ns3_abstract_operation()
        return ns3_abstract_operation_list

    def concatenate_ns3_abstract_operation(self):
        ns3_abstract_operation = {"ns3:AbstractOperation": "**ns3_abstract_operation_dict"}
        ns3_abstract_operation["ns3:AbstractOperation"] = self.concatenate_ns3_abstract_operation_dict()
        return ns3_abstract_operation

    def concatenate_ns3_abstract_operation_dict(self):
        ns3_abstract_operation_dict = {"@uri": "http://localhost:8000/Operation/AbstractOperation/00000001",
                                       "ns3:DeviceList": "**ns3_device"}
        ns3_abstract_operation_dict["ns3:DeviceList"] = self.concatenate_ns3_device()
        return ns3_abstract_operation_dict

    def concatenate_ns3_device(self):
        ns3_device = {"ns3:Device": []}
        ns3_device = self.recursive_append(block=ns3_device, multi_block=self.append_ns3_device_list(), key="ns3:Device")
        return ns3_device

    def append_ns3_device_list(self):
        ns3_device_list = {"@seq": "*device_sequence",
                           "ns3:SerialNumber": "*serial_number",
                           "ns3:FunctionList": "**ns3_function"}
        print('input *device_sequence[1,2,...,n]:')
        ns3_device_list["@seq"] = input()
        print('input *serial_number: ')
        ns3_device_list["ns3:SerialNumber"] = input()
        ns3_device_list["ns3:FunctionList"] = self.concatenate_ns3_function()
        return ns3_device_list

    def concatenate_ns3_function(self):
        ns3_function = {"ns3:Function": []}
        ns3_function = self.recursive_append(block=ns3_function, multi_block=self.append_ns3_function_list(), key="ns3:Function")

    def append_ns3_function_list(self):
        ns3_function_list = {"@seq": "*function_sequence",
                             "ns3:FunctionName": "*function_name",
                             "ns3:Value": "*value"}
        print('input *function_sequence[1,2,...,n]: ')
        ns3_function_list["@seq"] = input()
        print('input *function_name: ')
        ns3_function_list["ns3:FunctionName"] = input()
        print('input *ns3_value: ')
        ns3_function_list["ns3:Value"] = input()
        return ns3_function_list

    def concatenate_ns4_after_condition(self):
        ns4_after_condition = {"ns4:AfterCondition": "**after_condtion_dict"}
        ns4_after_condition["ns4:AfterCondition"] = self.concatenate_ns4_after_condition_dict()
        return ns4_after_condition

    def concatenate_ns4_after_condition_dict(self):
        ns4_after_condition_dict = {"@decision_time": "*decision_time",
                                    "ns4:ContextList": "**ns4_context"}
        print('input decision_time[sec]:')
        ns4_after_condition_dict["@decision_time"] = input()
        ns4_after_condition_dict = self.concatenate_ns4_context()
        return ns4_after_condition_dict

    def concatenate_ns4_context(self):
        ns4_context = {"ns4:Context": "**ns4_context_dict"}
        ns4_context = self.concatenate_ns4_context_dict()
        return ns4_context

    def concatenate_ns4_context_dict(self):
        ns4_context_dict = {"@id": "*ns4_context_id",
                            "@uri": "*ns4_context_uri",
                            "ns4:DeviceConditionEquationList": None,
                            "ns4:DeviceList": "**ns4_device"}
        ns4_context_dict = replace_target_asterisk(block=ns4_context_dict, key="*ns4_context_id")
        ns4_context_dict = replace_target_asterisk(block=ns4_context_dict, key="*ns4_context_uri")
        ns4_context_dict["ns4:DeviceList"] = self.concatenate_ns4_device()
        return ns4_context_dict

    def concatenate_ns4_device(self):
        ns4_device = {"ns4:Device": []}
        ns4_device = self.recursive_append(block=ns4_device, multi_block=self.append_ns4_device_list(), key="ns4:Device")
        return ns4_device

    def append_ns4_device_list(self):
        ns4_device_list = {"@id": "*ns4_device_id",
                           "ns4:SerialNumber": "*ns4_serial_number",
                           "ns4:Function": "**ns4_function_name",
                           "ns4:Value": "**ns4_value"}
        print('ns4_device_id is:')
        ns4_device_list["@id"] = input()
        print('*ns4_serial_number is:')
        ns4_device_list["ns4:SerialNumber"] = input()
        ns4_device_list["ns4:Function"] = self.concatenate_ns4_function_name()
        ns4_device_list["ns4*Value"] = self.concatenate_ns4_value()

    def concatenate_ns4_function_name(self):
        ns4_function_name = {"ns4:FunctionName": "*function_name"}
        print('*function_name is:')
        ns4_function_name["ns4:FunctionName"] = input()
        return ns4_function_name

    def concatenate_ns4_value(self):
        ns4_value = {"@type": "*type",
                     "#text": "*text"}
        print("*type is [upper,equal,lower]:")
        ns4_value["@type"] = input()
        print("*text is [numeric,TRUE,FALSE]:")
        ns4_value["#text"] = input()
        return ns4_value

    def after_condition(self):
        pass

        self.after_condition_template = {"ns4:AfterCondition":
                                             {"@decision_time": "*decision_time",
                                              "ns4:ContextList":
                                                  {"ns4:Context":
                                                       {"@id": "1",
                                                        "@uri": "http://localhost:8000/Condition/Context/00000001",
                                                        "ns4:DeviceConditionEquationList": None,
                                                        "ns4:DeviceList":
                                                            {"ns4:Device": []}}}}}
        self.ns4_device_template = {"@id": "iLN",
                                    "ns4:SerialNumber": "*serial_number",
                                    "ns4:Function":
                                        {"ns4:FunctionName": "*function_name"},
                                    "ns4:Value":
                                        {"@type": "*type",
                                         "#text": "*text"}}

    def main(self):
        """set input and specify target_brank"""
        print('create service now')
        service = self.struct_service()
        print(service)


if __name__ == '__main__':
    ser_sct = ServiceStruct()
    ser_sct.main()
