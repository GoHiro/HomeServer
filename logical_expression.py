import os
import json
import pathlib
from pathlib import Path
from pprint import pprint as pprint


class file_listup:
    def listup(self):
        # Pathオブジェクトを生成
        path_to_homeserver = '/home/tth07095/PycharmProjects/HomeServer (コピー)/home_server'
        concrete_service_folder = './user/'
        p = Path(concrete_service_folder)

        # user以下のファイルとディレクトリを再帰的に取得
        # Path.glob(pattern)はジェネレータを返す。結果を明示するためlist化しているが、普段は不要。
        # print(list(p.glob("**/*.json")))
        temp_service_list = list(p.glob("**/*.json"))

        # PosixPathをリストに変換した変数service_listを返す
        service_list = []
        list_number = len(temp_service_list)
        for item in range(list_number):
            service_list.append(temp_service_list[item])
        return service_list

class logical:
    def __init__(self):
        # 相対パスの先頭につけて絶対パスを指定する
        self.path_to_json = os.getcwd()
        # self.path_to_json = '/home/tth07095/PycharmProjects/HomeServer (コピー)/home_server'
        # self.concrete_service_uri = 'user/A/service/concrete/service/Concrete_Service_A.json'
        self.service_list = []
        self.service_dict = {}

    def service_load(self):
        # Concrete_Service_A.jsonを読み込み機器のidによる論理式を組む

        # sevice_listの要素'url/user'を指定してサービスを,json_dictにそれぞれのurlをキーとして格納
        for ser in self.service_list:
            with open(self.path_to_json + '/' +str(ser), mode='r', encoding='utf-8') as conservice:
                json_data = json.load(conservice)
                self.service_dict.update({str(ser):json_data})

        return self.service_dict

    def context_load(self):
        # service_dictに存在するcontextのURI先のコンテキストを読み込み

        # service_dictからcontextのuriを抽出
        path_to_context ="""['ConcreteService']['ConditionOperationSetList']['ConditionOperationSet']['ns2:Condition']"""\
                         """['ns2:ContextGroupList']['ns2:ContextGroup']['ns2:ContextList']['ns2:Context']['@uri'"""


        # print(path_to_context)
        # print(self.service_list[0])
        name_context_uri =  (str(self.service_list[0])) + """']""" + path_to_context
        #print(name_context_uri)

        test = self.service_dict[str(self.service_list[0])]
        print(test)

        test = test['ConcreteService']
        print(test)
        """listupの再起処理を用いて対象のキーを指定する"""
        #print(self.service_dict[str(self.service_list[0]), 'ConcreteService'])
        #print(self.service_dict['user/A/service/concrete/service/Concrete_Service_A.json'])
        #print(self.service_dict[name_context_uri])


        return test

    def service_list_str(self):
        # file_listup.listupでサービスフォルダの.jsonを探索
        # サービスのuriを記した'Posixpath'オブジェクトをリスト'self.service_list'へ格納
        self.service_list = (file_listup.listup(self))

        list_num = len(self.service_list)
        service_list = []
        for ser in range(list_num):
            service_list.append(str(self.service_list[ser]))

        self.service_list = service_list
        #print(self.service_list)

        return self.service_list

    def main(self):

        # strにキャストした'service_list'を生成する
        print(self.service_list_str())

        #for ser in self.service_list:
        #    i = 0
        #    print(ser)

        # print('getcwd:  ', os.getcwd())
        # print(self.path_to_json + self.concrete_service_uri)
        # 現在userフォルダ内にあるサービス.jsonの読み込み、json_dataへ格納
        self.service_load()
        print(self.service_dict)
        print(self.context_load())





if __name__ == '__main__':
    logical=logical()
    logical.main()
