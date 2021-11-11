from itertools import count
import olympic.settings as settings
import analyzer.olap as olap
import analyzer.handler_requests as hr
import analyzer.string_operation as strops
import analyzer.file_converter as fc
import time

class OlapBrowser:
    def __init__(self):
        self.olap_model: olap.OlapModel = self.__connect_olap_model(settings.OLAP_MODEL_PATH)


    def __connect_olap_model(self, model_config):
        return olap.connect_olap_model(model_config)
    

    def get_olap_data(self, path_keywords_model, request_keywords_dict, type_output="table"):
        dict_inputs, list_outputs = hr.create_olap_params(path_keywords_model, request_keywords_dict)
        if not list_outputs:
            return self.__create_struct_output(
                error=True,
                msg_err="Тo output fields selected!",
                type_err="Error"
            )
        
        start_time = time.time()
        filter_data = self.olap_model.aggregations(dict_inputs, list_outputs).filter_data(list_outputs)
        print("(get_olap_data) time cur:", time.time() - start_time)

        if strops.string_equal(type_output, 'table'):
            return self.table_cells(filter_data.json())
        elif strops.string_equal(type_output, 'list'):
            pass

        return "it's ok boss!"


    def table_cells(self, olap_data):
        data = olap_data["cells"]
        result_data = list()

        if not data:
            return self.__create_struct_output(
                error=True,
                msg_err="No results were found for this request!",
                type_err="Info"
            )        

        list_headers = list(data[0].keys())
        result_data.append(list_headers)

        for item in data:
            temp = [item[header] for header in list_headers]
            result_data.append(temp)

        return self.__create_struct_output(
            error=False,
            msg_err="No errors",
            list_data=result_data[1:],
            header=result_data[0]
        )


    def set_aliases_header(self, header, file_path):
        data_json = fc.get_json_from_file(file_path)
        return list(map(
            lambda item: data_json[item],
            header
        ))
        

    def __create_struct_output(self, header=None, list_data=None, error=False,  msg_err="", type_err="No errors") -> dict:
        def __struct(header=[], cells=[], count=0, error=False, msg_err="", type_err="No errors"):
            return {
                "error" : error,
                "msg_err" : msg_err,
                "type_err" : type_err,
                "header" : header,
                "cells" : cells,
                "count" : count
            }
        
        if list_data:
            count = len(list_data)
        else:
            list_data, count =  list(), 0

        if not header: header = list()
            
        return __struct(
            header=header,
            cells=list_data, 
            count=count, 
            error=error, 
            msg_err=msg_err
        )
