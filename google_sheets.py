import json
import pandas as pd
import requests
import io
import certifi
import os
from typing import Optional, Tuple, Dict

class Url_Sheets:
    def __init__(self):
        self.conexao = False
        self.verif_conect()
        self.url = "key env"
        print(self.url)
        self.session = requests.Session()


    def verif_conect(self, url:str="http://www.google.com", timeout:int=5) -> bool:
        try:
            requests.get(url, timeout=timeout)
            self.conexao = True
            return True
        except requests.RequestException:
            self.conexao = False
            return False

    def fetch_csv(self, url:str) -> Optional[requests.Response]:
        try:

            response = self.session.get(url, verify=certifi.where(), timeout=10)
            response.raise_for_status()
            self.conexao = True
            return response

        except requests.RequestException as e:
            self.conexao = False
            return None

    def nomes_ids(self) -> Tuple[Optional[Dict], Optional[Dict]]:
        key = "key env"
        url = self.url + key
        response = self.fetch_csv(url)
        if not response:
            self.conexao = False
            return None, None
        df = pd.read_csv(io.StringIO(response.text))
        self.conexao = True
        return (dict(zip(df['NOME'], df['ID'])),
                dict(zip(df['NOME'], df['TELE'])))

    def ids_teles(self) -> Optional[Dict]:
        _, dic_teles = self.nomes_ids()

        if not dic_teles:
            return None

        self.conexao = bool(dic_teles)

        if os.path.exists('jsons/ids_teleg.json'):
            if dic_teles == json.load(open('jsons/ids_teleg.json', encoding='utf-8')):
                return json.load(open('jsons/ids_teleg.json', encoding='utf-8'))
            else:
                os.remove('jsons/ids_teleg.json')

        with open('jsons/ids_teleg.json', 'w', encoding='utf-8') as arq:
            json.dump(dic_teles, arq, indent=4, ensure_ascii=False)

        return dic_teles

    def titulos(self) -> Optional[list]:
        dic_nomes, _ = self.nomes_ids()

        if not dic_nomes:
            self.conexao = False
            return None

        self.conexao = True

        if os.path.exists('jsons/nomes_psicos.json'):
            if dic_nomes == json.load(open('jsons/nomes_psicos.json', encoding='utf-8')):
                return list(json.load(open('jsons/nomes_psicos.json', encoding='utf-8')).keys())
            else:
                os.remove('jsons/nomes_psicos.json')

        with open('jsons/nomes_psicos.json', 'w', encoding='utf-8') as arq:
            json.dump(dic_nomes, arq, indent=4, ensure_ascii=False)

        return list(dic_nomes.keys())



