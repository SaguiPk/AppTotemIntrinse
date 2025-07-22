from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.properties import StringProperty
from kivymd.uix.button import MDButton, MDButtonText

from datetime import datetime
import json
import os.path
import time
import telebot

from telas import *
from google_sheets import Url_Sheets


class MainApp(MDApp):
    def build(self):
        # VERIFICAR SE HÁ INTERNET --------------------------------------------
        self.psico = ''
        self.arq_nomes = None
        self.ids_teles = None
        self.txt_input_nome = StringProperty('')
        self.agora = datetime.now()

        self.sheets = Url_Sheets()
        self.update_nomes_psis()

        self.dic_dias = {0:'SEGUNDA-FEIRA', 1:'TERCA-FEIRA', 2:'QUARTA-FEIRA', 3:'QUINTA-FEIRA', 4:'SEXTA-FEIRA'}   #, 5:'SABADO', 6:'DOMINGO'}
        self.dic_meses = {1:'janeiro', 2:'fevereiro', 3:'março', 4:'abril', 5:'maio', 6:'junho', 7:'julho', 8:'agosto', 9:'setembro', 10:'outubro', 11:'novembro', 12:'dezembro'}

        return Builder.load_file('main.kv')

    def check_internet(self, time=0):
        if not self.sheets.verif_conect():
            home = self.root.ids['homepage']
            texto = home.ids['id_conexao']
            texto.color = (1, 0, 0, 1)
            texto.text = 'Sem conexão'

            home = self.root.ids['homepage']
            home.ids['id_but_home'].disabled = True
            home.ids['id_enviar'].disabled = True
            self.casa()
            return False
        else:
            home = self.root.ids['homepage']
            texto = home.ids['id_conexao']
            texto.color = (0, 1, 0, 1)
            texto.text = 'Conectado'

            home = self.root.ids['homepage']
            home.ids['id_but_home'].disabled = False
            home.ids['id_enviar'].disabled = False
            return True

    def update_nomes_psis(self):
        nomes_file = 'jsons/nomes_psicos.json'
        ids_file = 'jsons/ids_teleg.json'
        tempo_val = 46800  # 13 horas em segundos

        def ler_json(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)

        def salvar_json(file_path, data):
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)

        def sem_net():
            home = self.root.ids['homepage']
            texto = home.ids['id_conexao']
            texto.color = (1, 0, 0, 1)
            texto.text = 'Sem conexão'
            home.ids['id_but_home'].disabled = True
            home.ids['id_enviar'].disabled = True
            self.casa()

        def fetch_and_update():
            nomes_ids = self.sheets.nomes_ids()
            if not nomes_ids[0]:
                sem_net()
                return False
            salvar_json(nomes_file, nomes_ids[0])
            salvar_json(ids_file, nomes_ids[1])
            self.arq_nomes = list(nomes_ids[0].keys())
            self.ids_teles = nomes_ids[1]
            return True

        # Verifica se os arquivos existem
        if os.path.exists(nomes_file):
            # Verifica se o arquivo está fora da validade
            if time.time() - os.path.getmtime(nomes_file) > tempo_val:
                fetch_and_update()
            else:
                self.arq_nomes = list(ler_json(nomes_file).keys())
                self.ids_teles = ler_json(ids_file)
        else:
            fetch_and_update()

    def atualizar_hora(self, dt):
        self.agora = datetime.now()
        self.hora_formatada = self.agora.strftime("%H:%M")
        self.label_hr.text = self.hora_formatada


    def on_start(self):
    # RELOGIO E DATA ---------------------------------------------------------------------

        label_dia = self.root.ids['homepage']
        label_dia = label_dia.ids['id_dia']

        if self.agora.weekday() >= 5:  # Se for sábado ou domingo
            label_dia.text = f'final de semana {self.agora.day} de {self.dic_meses[self.agora.month]} de {self.agora.year}' #dia4
        else:
            label_dia.text = f'{self.dic_dias[self.agora.weekday()].lower()}, {self.agora.day} de {self.dic_meses[self.agora.month]} de {self.agora.year}'  # dia4

        self.label_hr = self.root.ids['homepage']
        self.label_hr = self.label_hr.ids['id_horario']

        Clock.schedule_interval(self.atualizar_hora, 1)

    # FAZ A CONEXAO COM A PLANILHA --------------------------------------------------------
        self.psico_select = {} # dict armazena os buts_psic selecionado com o nome do psico

        conexao = self.sheets.conexao
        if conexao:
            home = self.root.ids['homepage']
            texto = home.ids['id_conexao']
            texto.color = (0,1,0,1)
            texto.text = 'Conectado'
            home = self.root.ids['homepage']
            home.ids['id_but_home'].disabled = False
            home.ids['id_enviar'].disabled = False
        else:
            home = self.root.ids['homepage']
            texto = home.ids['id_conexao']
            texto.color = (1,0,0,1)
            texto.text = 'Sem conexão'
            home = self.root.ids['homepage']
            home.ids['id_but_home'].disabled = True
            home.ids['id_enviar'].disabled = True

        def selecionar(but):
            ps = self.root.ids['psicos']
            self.psico = but.id # extrai o nome do psico
            nome_cliente = self.root.ids['nomecliente']
            msg_erro = nome_cliente.ids['msg_erro']
            msg_erro.text = 'DIGITE SEU [b]NOME[/b] E FAÇA O CHECK-IN'
            gerenciador_tela = self.root.ids['screen_manager']
            gerenciador_tela.current = 'nomecliente'


    # CRIA OS BOTÕES COM OS NOMES DOS PACIENTES ---------------------------------------
        if conexao:
            for psico in self.arq_nomes:
                but = MDButton(MDButtonText(text=f'{psico}', bold=True, pos_hint={'center_x':.5, 'center_y': .5}, theme_font_size="Custom", font_size='30', theme_text_color="Custom", text_color=(130/255, 20/255, 235/255, 1), theme_font_name='Custom', font_name='Gotham-Rounded-Medium'), style="elevated", theme_bg_color="Custom", md_bg_color='white', radius=[11,], theme_width="Custom", height="70dp", size_hint_x= 0.5)
                but.id = f'{psico}'
                page_psicos =self.root.ids['psicos']
                page_psicos.ids['main_scroll'].add_widget(but)
                but.bind(on_press=lambda x: selecionar(x))
                self.psico_select[but] = psico
        else:
            home = self.root.ids['homepage']
            home.ids['id_but_home'].disabled = True

    def mudar_tela(self, id_tela):
        tela_psicos = self.root.ids['psicos']
        gerenciador_tela = self.root.ids['screen_manager']
        gerenciador_tela.current = id_tela

    def voltar(self, time=0):
        if self.root.ids['screen_manager'].current == 'enviomsg':
            gerenciador_tela = self.root.ids['screen_manager']
            nome_cliente = self.root.ids['nomecliente']
            input = nome_cliente.ids['id_input']
            envio_msg = self.root.ids['enviomsg']
            texto_msg = envio_msg.ids['id_msg']
            nome_cliente = self.root.ids['nomecliente']
            msg_erro = nome_cliente.ids['msg_erro']
            msg_erro.text = ' '
            texto_msg.text = ''
            input.text = ''
            gerenciador_tela.current = 'homepage'

    def casa(self, time=0):
        gerenciador_tela = self.root.ids['screen_manager']
        nome_cliente = self.root.ids['nomecliente']
        input = nome_cliente.ids['id_input']
        envio_msg = self.root.ids['enviomsg']
        texto_msg = envio_msg.ids['id_msg']
        nome_cliente = self.root.ids['nomecliente']
        msg_erro = nome_cliente.ids['msg_erro']
        msg_erro.text = 'DIGITE SEU [b]NOME[/b] E FAÇA O CHECK-IN'
        texto_msg.text = ''
        input.text = ''
        self.txt_input_nome = None
        self.psico = None
        gerenciador_tela.current = 'homepage'

    def verificador(self, nome_paciente):
        self.txt_input_nome = nome_paciente.text

        # Verificar se é final de semana // OK - PARA TESTE //
        if self.agora.weekday() >= 5:
            nome_cliente = self.root.ids['nomecliente']
            msg_erro = nome_cliente.ids['msg_erro']
            msg_erro.text = 'FINAL DE SEMANA  ;) '
            msg_erro.color = (0, 1, 0, 1)
            Clock.schedule_once(callback=lambda dt: (setattr(msg_erro, 'text', 'DIGITE SEU [b]NOME[/b] E FAÇA O CHECK-IN'),setattr(msg_erro, 'color', (1, 1, 1, 1))), timeout=5)
        # Hoje é DIA UTIL ------
        else:
            # Verifica se os campos estão vazios, se não estiver vazio:
            if self.txt_input_nome != '' and isinstance(self.txt_input_nome, str):
                self.paciente = nome_paciente.text
                print(f'Campos Preenchidos: nome {self.paciente}')

                tela_enviomsg = self.root.ids['enviomsg']
                id_msg = tela_enviomsg.ids['id_msg']
                id_msg.text = ''

                try:
                    # Texto de resposta
                    id_msg.text = (f'[size=70]Bem Vindo {self.paciente.upper()}[/size]\n\n'  
                                   f'[size=50]Sua Psico já foi avisada ![/size]\n')

                    token = 'key env'
                    bot = telebot.TeleBot(token=token)
                    bot.send_message(chat_id=self.ids_teles[self.psico], text=f'{self.paciente.upper()}')  # text=f'{nome_paciente.text.upper()}')
                    Clock.schedule_once(callback=self.voltar, timeout=10)

                except Exception as e:  # SE FALAHAR O ENVIO
                    # se der erro verificar a internt
                    id_msg.text = (f'[size=70][color=ff0000]ERRO DE CONEXÃO[/color][/size]\n'
                                   f'[size=50]Consulte a recepção por gentileza ;)[/size]')

                    Clock.schedule_once(callback=self.check_internet, timeout=10)

                # TROCAR PARA ULTIMA TELA ----------------------
                gerenciador_tela = self.root.ids['screen_manager']
                gerenciador_tela.current = 'enviomsg'  # trocar tela ------
                # limpar compos textos ---------
                nome_paciente.text = ''
                self.psico = None  # limpar var.psico.selec
                self.paciente = ''


            # Tratar a situação de campos vazios
            else:
                print('campos não preenchidos')
                # Se o campo <nome_input> vazio e <hora_input> preenxido
                if self.txt_input_nome == '' and isinstance(self.txt_input_nome, str):
                    nome_cliente = self.root.ids['nomecliente']
                    msg_erro = nome_cliente.ids['msg_erro']
                    msg_erro.text = 'CAMPO NOME VAZIO'
                    msg_erro.color = (1, 0, 0, 1)
                    Clock.schedule_once(callback=lambda dt: (setattr(msg_erro, 'text', 'DIGITE SEU [b]NOME[/b] E FAÇA O CHECK-IN'), setattr(msg_erro, 'color', (1,1,1,1))), timeout=5)

    def atualizar(self):
        #print('atualizar')
        self.but = None
        for widget in self.dialog.walk():
            if isinstance(widget, MDButton) and widget.id == 'atualizar':
                widget.theme_line_color = 'Custom'
                widget.line_color = 'red'
                self.but = widget
        def inic_atual(time=0):
            lista_arquivos = None
            # pegar os arquivos do diretorio nomes_psicos.json, ids_teleg.json, acessar a pasta agendas e limpá-la, e depois reinstalar o que foi removido
            if os.path.exists('jsons/nomes_psicos.json'):
                os.remove('jsons/nomes_psicos.json')
            if os.path.exists('jsons/ids_teleg.json'):
                os.remove('jsons/ids_teleg.json')

            #print(lista_arquivos)
            self.update_nomes_psis()
            #print('atualização finalizada')
            self.but.line_color = 'green'

        Clock.schedule_once(inic_atual, 1)


MainApp().run()
