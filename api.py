import requests
import json


def select_character(json, character_job):
    for character_json in json:
        if character_job not in character_json['jobGrowName']:
            continue
        elif character_json['level'] != 110:
            continue
        else:
            return character_json


class df_api:

    all_jobs = ['베가본드', '아수라', '버서커']

    def __init__(self, api_key=None):
        self.api_key = api_key

    def api_basic_info(self, character_name, character_job):
        res = requests.get('https://api.neople.co.kr/df/servers/all/characters?characterName=' + character_name
                           + '&apikey=' + self.api_key)

        if len(res.json()['rows']) == 1:
            return res.json()['rows'][0]
        else:
            return select_character(res.json()['rows'], character_job)

    def api_basic_info_get_all(self, character_list):
        for character in character_list:
            character.job = next(job for job in self.all_jobs if job in character.job)
            character_api = self.api_basic_info(character.name, character.job)
            character.server = character_api['serverId']
            character.job = character_api['jobGrowName']
            character.character_id = character_api['characterId']

        return character_list

    def api_character_info(self, character):
        res = requests.get('https://api.neople.co.kr/df/servers/' + character.server +
                            '/characters/' + character.character_id + '/status?apikey='
                            + self.api_key)

        return res.json()

    def api_character_info_get_all(self, character_list):

        for character in character_list:
            character_api = self.api_character_info(character)
            character.guild = character_api['guildName']
            character.adventureName = character_api['adventureName']

            for stat in character_api['status']:
                if stat['name'] == '모험가 명성':
                    character.ms = stat['value']

        return character_list



