from django.http.request import QueryDict
import olympic.settings as st
import analyzer.string_operation as stroperation
import analyzer.file_converter as fc
import analyzer.handler_requests as hr
import analyzer.olap as olap



class ReceivedDataAggregator:


    def __init__(self, file_path):
        '''
        /* 
        /* 
        /* 
        '''
        data = fc.get_json_from_file(file_path)

        self.__dict_keys = None
        self.__keyword_types_str = set(data["types_str"]["data"])
        self.__keyword_types_int = set(data["types_int"]["data"])
        self.__keyword_types_float = set(data["types_float"]["data"])
        self.__keyword_types_bool = set(data["types_bool"]["data"])
        self.__keyword_types_switch = set(data["types_switch"]["data"])
        self.__check_output_keywords = set(data["output_keywords"]["data"])

    
    def get_processed_data(self, data: QueryDict) -> dict:
        self.__dict_keys = self._get_dict_fillters(data.dict())
        self.__uniq_sex_key(self.__dict_keys)
        return self.__dict_keys


    def _get_dict_fillters(self, data: dict) -> dict:
        result_dict_keys = self.__create_empty_dict_keys()

        for key in data.keys():
            if key in self.__keyword_types_str:
                result_dict_keys[key] = self.__processing_str_type(data[key])
            elif key in self.__keyword_types_int:
                result_dict_keys[key] = self.__processing_int_type(data[key])
            elif key in self.__keyword_types_float:
                result_dict_keys[key] = self.__processing_float_type(data[key])
            elif key in self.__keyword_types_bool:
                result_dict_keys[key] = self.__processing_bool_type(data[key])
            elif key in self.__keyword_types_switch:
                result_dict_keys[key] = self.__processing_switch_type(data[key])
            elif key in self.__check_output_keywords:
                result_dict_keys[key] = self.__processing_output_keywords(data[key])
            else:
                result_dict_keys[key] = None
        
        return result_dict_keys

    
    def __create_empty_dict_keys(self) -> dict:
        set_keys = self.__keyword_types_str | self.__keyword_types_int | self.__keyword_types_float | self.__keyword_types_bool | self.__keyword_types_switch | self.__check_output_keywords
        return { key : None for key in set_keys}
                                
        
    def __processing_str_type(self, data):
        return data if data else None


    def __processing_int_type(self, data):
        return stroperation.convert_str_to_int(data) if data and stroperation.check_int(data) else None
        

    def __processing_float_type(self, data):
        return stroperation.convert_str_to_float(data) if data and stroperation.check_float(data) else None

    
    def __processing_bool_type(self, data):
        return stroperation.convert_str_to_bool(data) if data and stroperation.check_bool(data) else None

    
    def __processing_switch_type(self, data):
        return stroperation.convert_str_to_switch(data) if data and stroperation.check_switch(data) else None

    
    def __processing_output_keywords(self, data):
        return stroperation.convert_str_to_switch(data) if data and stroperation.check_switch(data) else None


    def __uniq_sex_key(self, data: dict):
        if data["keyword_sex_f"] is None  and data["keyword_sex_m"] is None or data["keyword_sex_f"] == True  and data["keyword_sex_m"] == True:
            data["keyword_sex"] = None
        elif data["keyword_sex_f"] == True  and data["keyword_sex_m"] is None:
            data["keyword_sex"] = 'F'
        elif data["keyword_sex_f"] is None  and data["keyword_sex_m"] == True:
            data["keyword_sex"] = 'M'
        
        data.pop("keyword_sex_f", 0)
        data.pop("keyword_sex_m", 0)


    def create_alias_dict(self, data: dict, alias_file_name: str) -> dict:
        list_alias = fc.get_json_from_file(alias_file_name)
        result_dict = dict()
        result_dict["main"] = []
        create_pair = lambda key, val: {"name" : key, "value" : val} if list_alias["is_crete_key_value"] else lambda key, val: {key : val}

        for alias in list_alias["data_keys"]:
            alias["group"] = "main" if not alias["group"] else alias["group"]
            if alias["group"] not in result_dict:
                result_dict[alias["group"]] = []
            result_dict[alias["group"]].append(create_pair(alias["new_name"], data[alias["old_name"]]))

        return result_dict


    def filter_active_keys(self, data: list) -> list:
        return list(filter(
            lambda el: el["value"] is not None,
            data
        ))
        

def create_olap_params(keywords_path : str, keywords_dict : dict):
    test = ReceivedDataAggregator(keywords_path)
    data = test.get_processed_data(keywords_dict)
    data = test.create_alias_dict(data, st.ALIAS_KEYWORDS_FILE_PATH)
    list_keys = list(data.keys())
    list_keys.remove("out"); list_keys.remove("main")
    cuts = {item: test.filter_active_keys(data[item]) for item in list_keys}
    outs = [item["name"] for item in test.filter_active_keys(data["out"])]
    return cuts, outs

