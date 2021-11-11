import requests
import analyzer.file_converter as fc
from itertools import groupby
from operator import itemgetter
import analyzer.olap_exceptions as olapexc
import collections


class OlapData:
    def __init__(self, url=None, model=None, outputs_fields=None, aggregates=None) -> None:

        if url is not None:
            self.olap_data = requests.get(url).json()
        elif model is not None:
            self.olap_data = model

        self.outputs_fields = outputs_fields
        self.aggregates = aggregates
        self.__measures = list()
        for fields in self.outputs_fields:
            if fields in self.aggregates:
                self.__measures.append(fields)

        for measure in self.__measures:
            self.outputs_fields.remove(measure)


    def get_cells(self):
        return self.olap_data["cells"][:]


    def filter_data(self, outputs_fields):
        model = self.olap_data.copy()

        if outputs_fields:
            model["cells"] = self.__groupby_data_structs(model["cells"], outputs_fields)

        return OlapData(
            url=None, 
            model=model, 
            outputs_fields=self.outputs_fields + self.__measures,
            aggregates=self.aggregates
        )


    def __groupby_data_structs(self, data, sequence_keys):
        list_structs = list()

        data  = sorted(data, key=itemgetter(*sequence_keys))
        for keys, values in groupby(data, key = itemgetter(*sequence_keys)):
            if not isinstance(keys, collections.Iterable) or isinstance(keys, str):
                keys = [keys]
            
            struct = self.__create_struct(list(sequence_keys), tuple(keys))
            self.__sum_measures(struct, values)
            list_structs.append(struct)

        return list_structs


    def __create_struct(self, keys, values):
        struct = {}

        for i in range(len(keys)):
            struct[keys[i]] = values[i]
        for measure in self.__measures:
            struct[measure] = 0

        return struct


    def __sum_measures(self, struct, data):
        for item in data:
            for measure in self.__measures:
                struct[measure] += item[measure]


    def json(self):
        return self.olap_data


    def table(self):
        data = self.olap_data["cells"]
        result_data = list()

        if data:
            list_headers = list(data[0].keys())
            result_data.append(list_headers)

        for item in data:
            temp = [item[header] for header in list_headers]
            result_data.append(temp)


        return result_data


class OlapModel:

    def __init__(self, data_model_settings):
        self.data_settings = None
        self.aggregations_field = None
        self.connect(data_model_settings)


    def connect(self, data_model_settings):
        self.data_settings = data_model_settings
        self.aggregations_field = self.data_settings["aggregates"]


    def close(self):
        self.data = None
        self.aggregations_field = None


    def aggregations(self, dict_cuts_options, list_outputs_fields) -> OlapData:
        if not list_outputs_fields:
            raise olapexc.OlapInputDataException(
                "The list list_outputs_fields is empty!" +
                " The list list_outputs_fields must contain at least 1 output field"
            )

        cuts_url = self.get_cuts(dict_cuts_options)
        drilldown_url = self.get_drilldown(list_outputs_fields, dict_cuts_options)
        url = self.__get_aggregations_model_url(cuts_url, drilldown_url)

        return OlapData(
            url=url, 
            model=None, 
            outputs_fields=list_outputs_fields, 
            aggregates=self.aggregations_field
        )


    def __get_base_url(self):
        return self.data_settings["metadata"]["base_url"]


    def __get_aggregations_model_url(self, cuts_url:str=None, drilldown_url:str=None):
        base_url_aggregations = self.__get_base_url() + "/aggregate?"
        url_options = self.__get_url_options_model(cuts_url, drilldown_url)
        return base_url_aggregations + url_options

    
    def __get_url_options_model(self, cuts_url=None, drilldown_url=None):
        url_cuts = "&" + cuts_url if cuts_url else ""
        url_drilldown = "&" + drilldown_url if drilldown_url else ""

        return url_cuts + url_drilldown


    def get_cuts(self, dict_cuts):
        list_cuts = self.__create_list_cuts(self.data_settings["dimensions"], dict_cuts)
        return self.__get_url_format_cuts(list_cuts)


    def __get_url_format_cuts(self, list_cuts: list) -> str:
        return "cut=" + "|".join(list_cuts) if list_cuts else ""


    def __create_list_cuts(self, dimensions_list, dict_cuts):
        list_cuts = list()

        for dim in dimensions_list:
            fields_curr_dim = dim["fields"]

            for field in fields_curr_dim:
                hierarchy_val = self.__create_hierarchy_val_url(field, dict_cuts[dim["name"]])

                if hierarchy_val:
                    list_cuts.append(dim["name"] + hierarchy_val)
        
        return list_cuts


    def __create_hierarchy_val_url(self, dict_field, list_dicts_fields):
        for item in list_dicts_fields:
            if item["name"] == dict_field["name"]:
                return "@" + dict_field["hierarchy"] + ":" + self.__format_url_value(str(item["value"]))
        
        return ""

    
    def __format_url_value(self, str_value):
        parts = str_value.split()
        return "+".join(parts)


    def get_drilldown(self, list_field, dict_cuts):
        dict_all_fields = self.__create_dict_all_field(list_field, dict_cuts)
        list_drilldowns_pair = self.__create_list_drilldowns_pair(dict_all_fields)
        return self.__get_url_format_drilldown(list_drilldowns_pair)


    def __create_dict_all_field(self, list_field, dict_cuts):
        # add field from dict cuts field
        dict_all_fields = {key : [item["name"].split('.')[1] for item in value] for key, value in dict_cuts.items()}

        # add field from list outputs field
        for field in list_field:
            if field not in self.aggregations_field:
                parts_field = field.split('.')
                dict_all_fields[parts_field[0]].append(parts_field[1])

        # leave only unique fields
        dict_all_fields = {key : list(set(value)) for key, value in dict_all_fields.items()}

        return dict_all_fields

    
    def __create_list_drilldowns_pair(self, dict_all_fields):
        # the list_drilldowns_pair must contain sublists containing two elements: axis and last level
        list_drilldowns_pair = list()
        # the list_drilldowns_pair must contain dicts containing struct: 
        # {"name" : str, fields: list, "base_drilldown" : str, "levels" : list }
        list_dims_model = self.data_settings["dimensions"]

        for dim in list_dims_model:
            key, reverse_levels = dim["name"], dim["levels"][::-1], 
            for level in reverse_levels:
                if level in dict_all_fields[key]:
                    list_drilldowns_pair.append([key, level])
                    break
        
        return list_drilldowns_pair


    def __get_url_format_drilldown(self, list_drilldowns_pair):
        result_url = "drilldown="
        # the list contains lines that characterize the axis and the required last level for this axis
        list_pair = [":".join(pair) for pair in list_drilldowns_pair]
        # return combining all necessary axes into one request for drilldown
        return result_url + "|".join(list_pair) if list_pair else ""


def connect_olap_model(filename_model: str) -> OlapModel:
    model = fc.get_json_from_file(filename_model)
    cube = OlapModel(model)
    return cube