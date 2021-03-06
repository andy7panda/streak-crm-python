# -*- coding: utf-8 -*-

import json
import requests
from requests.auth import HTTPBasicAuth

try:
    from keys import TEST_API_KEY
except:
    TEST_API_KEY = 'YOU_API_KEY_HERE'


def flush_attributes(obj):
    tmp = obj.__dict__['streak_connection']
    obj.__dict__ = {}
    setattr(obj, 'streak_connection', tmp)
    return obj


def add_attributes(attr_dict: dict, obj: object):
    """
    Takes obj and dict, creates obj properties as dict keys:values , returns obj updated
    # >>> add_attributes({'fox_count': 15}, animal_counter)
    # >>> animal_counter.fox_count == 15
    # True
    :param attr_dict: dict with attrs
    :param obj: object
    :return: obj updated
    """
    for key, value in attr_dict.items():
        setattr(obj, key, value)
    return obj


# def api_get(self, request_path):
# return self.streak_connection.get_api_data(request_path)


class StreakConnection:
    def __init__(self, api_key=TEST_API_KEY):
        self.settings = self.Settings(api_key)

    def __repr__(self):
        return '<Streak Connection Object>'

    class Settings:
        def __init__(self, api_key, api_endpoint='https://www.streak.com/api/v1/'):
            self.api_key = api_key
            self.api_endpoint = api_endpoint

    def get_api_data(self, api_path: str):
        """
        Merges api_endpoint with api_path and sends GET request
        :param api_path: string
        :return: object
        """
        result = None
        api_full_path = self.settings.api_endpoint + api_path
        print('[API GET]', api_full_path)
        try:
            result = requests.get(api_full_path, auth=HTTPBasicAuth(self.settings.api_key, ''))
        except requests.HTTPError:
            print('[HTTP GET] Error')
            exit()
        else:
            result = json.loads(result.text)
        return result

    def put_api_data(self, api_path: str, settings: dict):
        """
        Merges api_endpoint with api_path and sends PUT request
        :param api_path: string
        :return: object
        """
        result = None
        api_full_path = self.settings.api_endpoint + api_path
        print('[API PUT]', api_full_path)
        try:
            result = requests.put(api_full_path, data=settings, auth=HTTPBasicAuth(self.settings.api_key, ''))
        except requests.HTTPError:
            print('[HTTP PUT] Error')
            exit()
        else:
            result = json.loads(result.text)
        return result

    def delete_api_data(self, api_path: str):
        """
        Merges api_endpoint with api_path and sends DELETE request
        :param api_path: string
        :return: object
        """
        result = None
        api_full_path = self.settings.api_endpoint + api_path
        print('[API DELETE]', api_full_path)
        try:
            result = requests.delete(api_full_path, auth=HTTPBasicAuth(self.settings.api_key, ''))
        except requests.HTTPError:
            print('[HTTP DELETE] Error')
            exit()
        else:
            result = json.loads(result.text)
        return result

    def post_api_data(self, api_path: str, settings: dict):
        """
        Merges api_endpoint with api_path and sends POST request
        :param api_path: string
        :return: object
        """
        result = None
        api_full_path = self.settings.api_endpoint + api_path
        print('[API POST]', api_full_path)
        try:
            result = requests.post(api_full_path, data=json.dumps(settings),
                                   auth=HTTPBasicAuth(self.settings.api_key, ''),
                                   headers={'Content-Type': 'application/json'})
        except requests.HTTPError:
            print('[HTTP POST] Error')
            exit()
        else:
            result = json.loads(result.text)
        return result

    def user_get_me(self):
        """
        Returns current authorized User (myself)
        :return: User
        """
        request_path = 'users/me'
        user_me_data = self.get_api_data(request_path)
        # creates new User instance as assigns keys:values from server response as it's properties
        user = add_attributes(user_me_data, User(self))
        return user

    def user_get(self, user_key):
        """
        Gets User data by userKey
        :param user_key: string
        :return: User
        """
        request_path = 'users/' + user_key
        user_data = self.get_api_data(request_path)

        # if server response has error code
        if 'success' in user_data.keys():
            raise Exception(user_data['error'])

        user = add_attributes(user_data, User(self))
        return user

    def pipeline_get_all(self):
        """
        Gets all pipelines
        :return: list of Pipelines objects
        """
        pipelines_list = []
        request_path = 'pipelines/'
        pipelines_data = self.get_api_data('pipelines/')
        for pipeline_dict in pipelines_data:
            pipelines_list.append(add_attributes(pipeline_dict, Pipeline(self)))
        return pipelines_list

    def pipeline_get(self, pipeline_key: str):
        """
        Gets Pipeline by key
        :param pipeline_key:
        :return: Pipeline instance
        """
        if not pipeline_key:
            raise Exception('[!] Empty pipeline key, please supply one')

        pipeline_data = self.get_api_data('pipelines/' + pipeline_key)

        if 'success' in pipeline_data.keys():
            raise Exception(pipeline_data['error'])

        pipeline = add_attributes(pipeline_data, Pipeline(self))
        return pipeline

    def pipeline_create(self, pipeline_params: dict):
        """
        Creates and returns Pipeline with given params
        :param pipeline_params: dict of params
        :return: newly created Pipeline instance
        """
        pipeline_data = self.put_api_data('pipelines/', pipeline_params)

        if 'success' in pipeline_data.keys():
            raise Exception(pipeline_data['error'])

        new_pipeline = self.pipeline_get(pipeline_data['pipelineKey'])

        print('New Pipeline created')

        return new_pipeline

    def pipeline_delete(self, pipeline_key: str):
        """
        Deletes pipeline by key
        :param pipeline_key:
        :return:
        """
        response_on_delete = self.delete_api_data('pipelines/' + pipeline_key)

        if not response_on_delete['success']:
            raise Exception('Failed to delete Pipeline')
        else:
            print('Pipeline deleted')

    def pipeline_edit(self, pipeline_key: str, pipeline_params: dict):
        pipeline_update_result = self.post_api_data('pipelines/' + pipeline_key, pipeline_params)

        if 'success' in pipeline_update_result.keys():
            raise Exception(pipeline_update_result['error'])

        print('Pipeline updated')
        updated_pipeline = self.pipeline_get(pipeline_update_result['pipelineKey'])
        return updated_pipeline

    def box_get_all(self):
        boxes_list = []
        boxes_data = self.get_api_data('boxes/')
        for box_data in boxes_data:
            boxes_list.append(add_attributes(box_data, Box(self)))
        return boxes_list

    def box_get_all_in_pipeline(self, pipeline_key: str):
        boxes_list = []
        boxes_data = self.get_api_data('pipelines/%s/boxes' % pipeline_key)
        for box_data in boxes_data:
            boxes_list.append(add_attributes(box_data, Box(self)))
        return boxes_list

    def box_get(self, box_key: str):
        """
        Gets Box by key
        :param box_key:
        :return: Pipeline instance
        """
        if not box_key:
            raise Exception('[!] Empty box key, please supply one')

        box_data = self.get_api_data('boxes/' + box_key)

        if 'success' in box_data.keys():
            raise Exception(box_data['error'])

        box = add_attributes(box_data, Box(self))
        return box

    def box_create(self, pipeline_key: str, box_params: dict):
        """
        Creates and returns Box with given params
        :param box_params: dict of params
        :return: newly created Pipeline instance
        """
        box_data = self.put_api_data('pipelines/%s/boxes' % pipeline_key, box_params)

        if 'success' in box_data.keys():
            raise Exception(box_data['error'])

        new_box = self.box_get(box_data['boxKey'])

        print('New Box created')
        return new_box

    def box_delete(self, box_key: str):
        """
        Deletes Box by key
        :param box_key:
        :return:
        """
        response_on_delete = self.delete_api_data('boxes/' + box_key)

        if not response_on_delete['success']:
            raise Exception('Failed to delete Box')
        else:
            print('Box deleted')

    def box_edit(self, box_key: str, box_params: dict):
        box_edit_result = self.post_api_data('boxes/' + box_key, box_params)

        if 'success' in box_edit_result.keys():
            raise Exception(box_edit_result['error'])

        print('Box updated')
        updated_box = self.box_get(box_edit_result['boxKey'])
        return updated_box

    def stage_get_all_in_pipeline(self, pipeline_key: str):
        stages_list = []
        stages_data = self.get_api_data('pipelines/%s/stages' % pipeline_key)
        for stage_data in stages_data.values():
            stages_list.append(add_attributes(stage_data, Stage(self, pipeline_key)))
        return stages_list

    def stage_get_specific_in_pipeline(self, pipeline_key: str, stage_key: str):
        stage_data = self.get_api_data('pipelines/%s/stages/%s' % (pipeline_key, stage_key))

        if 'success' in stage_data.keys():
            raise Exception(stage_data['error'])

        stage = add_attributes(stage_data, Stage(self, pipeline_key))
        return stage

    def stage_create_in_pipeline(self, pipeline_key: str, stage_params: dict):
        stage_data = self.put_api_data('pipelines/%s/stages' % pipeline_key, stage_params)

        if 'success' in stage_data.keys():
            raise Exception(stage_data['error'])

        new_stage = self.stage_get_specific_in_pipeline(pipeline_key, stage_data['key'])

        print('New Stage created')
        return new_stage

    def stage_delete_in_pipeline(self, pipeline_key: str, stage_key: str):
        response_on_delete = self.delete_api_data('pipelines/%s/stages/%s' % (pipeline_key, stage_key))

        if not response_on_delete['success']:
            raise Exception('Failed to delete Stage')
        else:
            print('Stage deleted')

    def stage_edit_in_pipeline(self, pipeline_key: str, stage_key: str, stage_params: dict):
        stage_edit_result = self.post_api_data('pipelines/%s/stages/%s' % (pipeline_key, stage_key), stage_params)

        if 'success' in stage_edit_result.keys():
            raise Exception(stage_edit_result['error'])

        print('Stage edited')
        stage_edited = self.stage_get_specific_in_pipeline(pipeline_key, stage_edit_result['key'])
        return stage_edited

    def field_get_all_in_pipeline(self, pipeline_key: str):
        field_list = []
        fields_data = self.get_api_data('pipelines/%s/fields' % pipeline_key)
        for field_data in fields_data:
            field_list.append(add_attributes(field_data, Field(self, pipeline_key)))
        return field_list

    def field_get_specific_in_pipeline(self, pipeline_key: str, field_key: str):
        field_data = self.get_api_data('pipelines/%s/fields/%s' % (pipeline_key, field_key))

        if 'success' in field_data.keys():
            raise Exception(field_data['error'])

        field = add_attributes(field_data, Field(self, pipeline_key))
        return field

    def field_create_in_pipeline(self, pipeline_key: str, field_params: dict):
        field_data = self.put_api_data('pipelines/%s/fields' % pipeline_key, field_params)

        if 'success' in field_data.keys():
            raise Exception(field_data['error'])

        new_field = self.field_get_specific_in_pipeline(pipeline_key, field_data['key'])

        print('New Field created')
        return new_field

    def field_delete_in_pipeline(self, pipeline_key: str, field_key: str):
        response_on_delete = self.delete_api_data('pipelines/%s/fields/%s' % (pipeline_key, field_key))

        if not response_on_delete['success']:
            raise Exception('Failed to delete Field')
        else:
            print('Field deleted')

    def field_edit_in_pipeline(self, pipeline_key: str, field_key: str, field_params: dict):
        field_edit_result = self.post_api_data('pipelines/%s/fields/%s' % (pipeline_key, field_key), field_params)

        if 'success' in field_edit_result.keys():
            raise Exception(field_edit_result['error'])

        print('Field edited')
        field_edited = self.field_get_specific_in_pipeline(pipeline_key, field_edit_result['key'])
        return field_edited

    def field_get_values_for_box(self, box_key: str):
        field_list = []
        fields_data = self.get_api_data('boxes/%s/fields' % box_key)
        for field_data in fields_data:
            field_list.append(add_attributes(field_data, Field(self, box_key)))
        return field_list

    def value_get_all_in_box(self, box_key: str):
        value_list = []
        values_data = self.get_api_data('boxes/%s/fields' % box_key)
        for value_data in values_data:
            # new_value = Value(self, box_key)
            # new_value.key = value_data['key']
            # if type(value_data['value']) ==
            value_list.append(add_attributes(value_data, Value(self, box_key)))
        return value_list

    def value_get_specific_in_box(self, box_key: str, field_key: str):
        value_data = self.get_api_data('boxes/%s/fields/%s' % (box_key, field_key))

        if 'success' in value_data.keys():
            raise Exception(value_data['error'])

        value = add_attributes(value_data, Value(self, box_key))
        return value

    def value_edit_in_box(self, box_key: str, field_key: str, field_params: dict):
        value_edit_result = self.post_api_data('boxes/%s/fields/%s' % (box_key, field_key), field_params)

        if 'success' in value_edit_result.keys():
            raise Exception(value_edit_result['error'])

        print('Value edited')
        value_edited = self.value_get_specific_in_box(box_key, value_edit_result['key'])
        return value_edited


class User:
    def __init__(self, streak_connection):
        self.streak_connection = streak_connection
        self.displayName = 'n/a'

    def __repr__(self):
        return '<User: \'%s>\'' % self.displayName

        # def reload(self):
        # print('Updating User...'),
        # self = self.streak_connection.user_get(self.userKey)
        # print('...done.')
        # return self


class Pipeline:
    def __init__(self, streak_connection):
        self.streak_connection = streak_connection
        self.name = ''
        self.pipelineKey = ''

    def __repr__(self):
        return '<Pipeline: \'%s>\'' % self.name

    def delete_self(self):
        self.streak_connection.pipeline_delete(self.pipelineKey)

        # def reload(self):
        # print('Updating Pipeline...'),
        # self = self.streak_connection.pipeline_get(self.pipelineKey)
        # print('...done.')
        # return self


class Box:
    def __init__(self, streak_connection):
        self.streak_connection = streak_connection
        self.name = ''
        self.pipelineKey = ''

    def __repr__(self):
        return '<Box: \'%s>\'' % self.name

    def delete_self(self):
        self.streak_connection.box_delete(self.boxKey)


class Stage:
    def __init__(self, streak_connection, pipeline_key):
        self.streak_connection = streak_connection
        self.pipeline_key = pipeline_key
        self.name = ''

    def __repr__(self):
        return '<Stage: \'%s>\'' % self.name

    def delete_self(self):
        self.streak_connection.stage_delete_in_pipeline(self.pipeline_key, self.key)


class Field:
    def __init__(self, streak_connection, pipeline_key):
        self.streak_connection = streak_connection
        self.pipeline_key = pipeline_key
        self.name = ''

    def __repr__(self):
        return '<Field: \'%s\'>' % self.name

    def delete_self(self):
        self.streak_connection.field_delete_in_pipeline(self.pipeline_key, self.key)


class Value:
    def __init__(self, streak_connection, box_key):
        self.streak_connection = streak_connection
        self.box_key = box_key
        self.value = ''

    def __repr__(self):
        return "<Value: '%s'>" % self.value


if __name__ == '__main__':
    pass
