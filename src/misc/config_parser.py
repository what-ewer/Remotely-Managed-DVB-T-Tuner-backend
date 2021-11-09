from configparser import ConfigParser as cfgParser


class ConfigParser:
    def parse_config(self, location, section):
        if len(location) > 0 and len(section) > 0:
            config_parser = cfgParser()
            config_parser.read(location)
            if config_parser.has_section(section):
                config_params = config_parser.items(section)
                db_conn_dict = {}
                for config_param in config_params:
                    key = config_param[0]
                    value = config_param[1]
                    db_conn_dict[key] = value
                return db_conn_dict
            return {}
        return {}
