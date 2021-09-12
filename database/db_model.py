import json


class JsonConverter:
    @staticmethod
    def convert_all(body, selected_class):
        json_body = json.loads(body)
        try:
            res = [selected_class(**v) for v in json_body]
        except Exception as e:
            print(e)
            return []

        return res

    @staticmethod
    def convert(body, selected_class):
        json_body = json.loads(body)
        try:
            res = selected_class(**json_body)
        except Exception as e:
            print(e)
            return []

        return res

    @staticmethod
    def check_json(body, selected_class):
        json_body = json.loads(body)
        try:
            res = [selected_class(**v) for v in json_body]
        except Exception as e:
            print(e)
            return []

        return json_body


class TunerStatus:
    def __init__(
        self,
        free_space,
        is_recording,
        current_recording_size,
        current_recording_time,
        **kwargs
    ):
        self.free_space = free_space
        self.is_recording = is_recording
        self.current_recording_size = current_recording_size
        self.current_recording_time = current_recording_time


class Settings:
    def __init__(self, recording_location, tvh_username, tvh_password, **kwargs):
        self.recording_location = recording_location
        self.tvh_username = tvh_username
        self.tvh_password = tvh_password


class RecordedFiles:
    def __init__(self, channel_id, program_name, record_size, start, end, **kwargs):
        self.program_name = program_name
        self.channel_id = channel_id
        self.record_size = record_size
        self.start = start
        self.end = end


class InformationNeeded:
    def __init__(
        self,
        changed_recording_order_list,
        changed_settings,
        need_recording_file_list,
        need_epg,
        **kwargs
    ):
        self.changed_recording_order_list = changed_recording_order_list
        self.changed_settings = changed_settings
        self.need_recording_file_list = need_recording_file_list
        self.need_epg = need_epg


class RecordOrders:
    def __init__(self, channel_id, start, end, **kwargs):
        self.channel_id = channel_id
        self.start = start
        self.end = end


class User:
    def __init__(self, login, password, **kwargs):
        self.login = login
        self.password = password


class EPG:
    def __init__(
        self,
        eventId,
        episodeId,
        channelName,
        channelUuid,
        channelNumber,
        start,
        stop,
        title,
        subtitle,
        summary,
        description,
        genre,
        nextEventId,
        **kwargs
    ):
        self.event_id = eventId
        self.episode_id = episodeId
        self.channel_name = channelName
        self.channel_uuid = channelUuid
        self.channel_number = channelNumber
        self.start = start
        self.stop = stop
        self.title = title
        self.subtitle = subtitle
        self.summary = summary
        self.description = description
        self.genre = genre
        self.next_event_id = nextEventId


class Channel:
    def __init__(self, id, name, multiplex_id, multiplex_name, **kwargs):
        self.id = id
        self.name = name
        self.multiplex_id = multiplex_id
        self.multiplex_name = multiplex_name
