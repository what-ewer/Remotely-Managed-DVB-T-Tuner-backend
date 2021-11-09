from flask import request, Response


class APIExecutor:
    def __init__(self, json_converter):
        self.json_converted = json_converter

    def execute_function(self, function, args=None, data_class=None, convert=True):
        res_args = self.__check_args(args)
        if isinstance(res_args, Response):
            return res_args
        elif data_class:
            json_data = self.__get_json(data_class, convert)
            if json_data:
                res_args.append(json_data)
            else:
                return Response(
                    "Required data for api doesn't provide needed class", status=400
                )

        return self.__get_function_response(function, res_args)

    def __get_function_response(self, function, args):
        return function(*args)

    def __check_args(self, args):
        args_values = []
        missing_args = []
        for arg in args:
            if arg == "username" or arg == "password":
                arg_val = request.authorization.get(arg)
            else:
                arg_val = request.args.get(arg)
            args_values.append(arg_val)
            if not arg_val:
                missing_args.append(arg)

        return (
            Response(f"Provide arguements for {missing_args}", status=400)
            if missing_args
            else args_values
        )

    def __get_json(self, data_class, convert):
        data = request.data
        if convert:
            return self.json_converter.convert_any(data, data_class)
        else:
            return self.json_converter.check_json(data, data_class)
