import json
import os


class ServiceStruct:
    def __init__(self):
        """Concrete Service dump from template"""
        self.service_name = "Concrete_Service_C_4"
        self.summary = "Light ON when human in the room"
        self.user_name = "C"
        self.condition_id = "Loh"
        self.context_uri = "http://localhost:8000/Condition/Context/00000005"
        self.priority = "1"

        self.service = \
            {
                "?xml": {
                    "@version": "1.0",
                    "@encoding": "UTF-8",
                    "@standalone": "yes"
                },
                "ConcreteService": {
                    "@uri": f"/user/C/service/concrete/service/{self.service_name}",
                    "@xmlns:ns2": "http://www.example.org/HNS/Service/ConcreteService/ConcreteCondition ",
                    "@xmlns": "http://www.example.org/HNS/Service/ConcreteService/ConcreteService ",
                    "@xmlns:ns4": "http://www.example.org/HNS/Service/ConcreteService/ConcreteAfterCondition ",
                    "@xmlns:ns3": "http://www.example.org/HNS/Service/ConcreteService/ConcreteOperation",
                    "CreatedDate": "2019-10-23T16:21:27.237+09:00",
                    "Summary": f"{self.summary}",
                    "AbstractServiceReference": {
                        "@uri": "http://localhost:8080/service/abstractservice/00000001"
                    },
                    "User": f"{self.user_name}",
                    "Name": f"{self.service_name}",
                    "Priority": f"{self.priority}",
                    "ConditionOperationSetList": {
                        "ConditionOperationSet": {
                            "ns2:Condition": {
                                "ns2:ConditionEquationList": {
                                    "ns2:ConditionEquation": f"{self.condition_id}"
                                },
                                "ns2:ContextGroupList": {
                                    "ns2:ContextGroup": {
                                        "@id": f"{self.condition_id}",
                                        "ns2:ContextEquationList": {
                                            "ns2:ContextEquation": f"{self.condition_id}"
                                        },
                                        "ns2:ContextList": {
                                            "ns2:Context": {
                                                "@id": f"{self.condition_id}",
                                                "@uri": f"{self.context_uri}",
                                                "ns2:DeviceList": {
                                                    "ns2:Device": [
                                                        {
                                                            "@id": "iLN",
                                                            "ns2:SerialNumber": "IRSensor C",
                                                            "ns2:Function": {
                                                                "ns2:FunctionName": "DetectionStatus"
                                                            },
                                                            "ns2:Value": {
                                                                "@type": "equal",
                                                                "#text": "TRUE"
                                                            }
                                                        },
                                                        {
                                                            "@id": "Tpb",
                                                            "ns2:SerialNumber": "TempSensor C",
                                                            "ns2:Function": {
                                                                "ns2:FunctionName": "RoomTemperatureMeasurement"
                                                            },
                                                            "ns2:Value": {
                                                                "@type": "upper",
                                                                "#text": "18"
                                                            }
                                                        }
                                                    ]
                                                },
                                                "ns2:DeviceConditionEquationList": None
                                            }
                                        }
                                    }
                                }
                            },
                            "ns3:Operation": {
                                "ns3:AbstractOperationGroupList": {
                                    "ns3:AbstractOperationGroup": {
                                        "ns3:AbstractOperationList": {
                                            "ns3:AbstractOperation": {
                                                "@uri": "http://localhost:8000/Operation/AbstractOperation/00000001",
                                                "ns3:DeviceList": {
                                                    "ns3:Device": [
                                                        {
                                                            "@seq": "1",
                                                            "ns3:SerialNumber": "Fan C",
                                                            "ns3:FunctionList": {
                                                                "ns3:Function": [
                                                                    {
                                                                        "@seq": "1",
                                                                        "ns3:FunctionName": "OperatingStatus",
                                                                        "ns3:Value": "ON"
                                                                    },
                                                                    {
                                                                        "@seq": "2",
                                                                        "ns3:FunctionName": "TemperatureSettingValue",
                                                                        "ns3:Value": "25"
                                                                    },
                                                                    {
                                                                        "@seq": "3",
                                                                        "ns3:FunctionName": "FanSpeed",
                                                                        "ns3:Value": "2"
                                                                    }
                                                                ]
                                                            }
                                                        }
                                                    ]
                                                }
                                            }
                                        }
                                    }
                                }
                            },
                            "ns4:AfterCondition": {
                                "@decision_time": "600",
                                "ns4:ContextList": {
                                    "ns4:Context": {
                                        "@id": "1",
                                        "@uri": "http://localhost:8000/Condition/Context/00000001",
                                        "ns4:DeviceConditionEquationList": None,
                                        "ns4:DeviceList": {
                                            "ns4:Device": {
                                                "@id": "te0",
                                                "ns4:SerialNumber": "TempSensor C",
                                                "ns4:Function": {
                                                    "ns4:FunctionName": "RoomTemperatureMeasurement"
                                                },
                                                "ns4:Value": {
                                                    "@type": "upper",
                                                    "#text": "18"
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }

    def main(self):
        with open(os.getcwd() + f'/{self.service_name}' + '.json', 'w') as f:
            json.dump(self.service, f, ensure_ascii=False, indent=4)



if __name__ == "__main__":
    ser_sct = ServiceStruct()
    ser_sct.main()