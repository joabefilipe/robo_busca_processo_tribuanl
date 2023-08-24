import requests
import re
import base64

from lxml import html

usuario = ''
senha = ''

session = requests.session()
session.verify = False

url_host = 'https://pjd.tjgo.jus.br/'

url_logon = f'{url_host}/LogOn'
url_pag_atual = f'{url_host}/Usuario?'
url_process = f'{url_host}/BuscaProcessoUsuarioExterno?'
url_arquivo = f'{url_host}/MovimentacaoArquivo?'
url_download_arquivo = f'{url_host}BuscaProcessoUsuarioExterno?'

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/114.0.0.0 Safari/537.36'

}

response_pagina_tribunal = session.get(url=url_host, headers=headers, verify=False)
response_pagina_tribunal.raise_for_status()

pjd_login = {'PaginaAtual': '7', 'Usuario': usuario, 'Senha': senha}
response_login = session.post(url=url_logon, headers=headers, data=pjd_login, verify=False)
response_login.raise_for_status()

params_atual = {'PaginaAtual': '7', 'a1': '729', 'a2': '2', 'a3': '', 'a4': '', 'a5': '',
                'LoginPronto': '5', 'hashFluxo': '1687261201117'}
response_pagina_atual = session.get(url=url_pag_atual, params=params_atual, headers=headers, verify=False)

process = ''
params_process = {'PaginaAtual': '2', 'ProcessoNumero': process, 'fluxo': 'menuPrincipal', 'PassoBusca': '0',
                  'ProcessoStatusCodigo': '0'}

response_process = session.get(url=url_process, headers=headers, params=params_process, verify=False)
response_process.raise_for_status()
root = html.fromstring(response_process.text)

process_id = root.xpath('//*[@id="processo_id"]')[0].attrib.get('value')

params_movement = {'Id_Processo': process_id, 'menuCentralProcesso': 'menuMovimentacaoProcesso'}
response_movement = session.get(url=url_process, headers=headers, params=params_movement, verify=False)
response_movement.raise_for_status()

root_movement = html.fromstring(response_movement.text)
movimentacoes = root_movement.xpath('//*[@id="tbodyListaMovimentacoes"]/tr')
dict_movimentacao = []
for tr in movimentacoes:
    movimentacao = tr.xpath('./*[contains(@id, "idmovnome")]//span/text()')[0]
    data_hora = tr.xpath('./*[contains(@id, "idmovdata")]/span/text()')[0]
    numero_movimentacao = tr.xpath('./*[contains(@id, "idmovnumero")]/text()')[0].strip()
    usuario = tr.xpath('./*[contains(@id, "idmovusuario")]/span/text()')

    dict_movimentacao.append({
        'id': numero_movimentacao,
        'movimentacao': movimentacao,
        'data': data_hora,
        'usuario': usuario[0] if usuario else "sem usuario",

    })

dict_arquivos = []
for tr in movimentacoes:
    todas_movimentacoes = tr.xpath('./td')[0].attrib.get('onclick').strip()
    id_movimentacao = re.search(r"detalhesMovimentacao\('(\d+)'", todas_movimentacoes).group(1)


    params_arquivo = {'PaginaAtual': '8', 'Id_Movimentacao': id_movimentacao}
    response_arquivo = session.get(url=url_arquivo, params=params_arquivo, headers=headers, verify=False)
    response_arquivo.raise_for_status()
    root_arquivo = html.fromstring(response_arquivo.text)
    script_movimentacao_arquivos = root_arquivo.xpath('.//script[contains(text(), "JSON.parse(")]/text()')
    if not script_movimentacao_arquivos:
        print('não tem')
        continue

    script_arquivos = script_movimentacao_arquivos[0]

    ids_movimentacoes_arquivos = re.findall('(?<=id":")(.*?)(?=",)', script_arquivos)
    ids_arquivos = re.findall('(?<=id_arquivo":")(.*?)(?=",)', script_arquivos)
    nomes_arquivos = re.findall('(?<=nome_arquivo":")(.*?)(?=",)', script_arquivos)
    tipos_arquivos = re.findall('(?<=arquivo_tipo":")(.*?)(?=",)', script_arquivos)
    usuarios_assinadores = re.findall('(?<=usuario_assinador":")(.*?)(?=",)', script_arquivos)
    hashs = re.findall('(?<=hash":")(.*?)(?=",)', script_arquivos)

    for hash, id_arquivo, nome_arquivo, tipo_arquivo, usuario_assinador, id_movimentacao_arquivo in \
            zip(hashs, ids_arquivos, nomes_arquivos, tipos_arquivos, usuarios_assinadores, ids_movimentacoes_arquivos):

        params_download = {'PaginaAtual': '6', 'Id_MovimentacaoArquivo': id_movimentacao_arquivo,
                           'hash': hash, 'CodigoVerificacao': 'true', 'blob': '1'}
        response_download = session.get(url=url_download_arquivo, params=params_download, headers=headers, verify=False)
        response_download.raise_for_status()

        arquivo_b64 = base64.b64encode(response_download.content).decode()

        dict_arquivos.append({
            'hash': hash,
            'id_arquivo': id_arquivo,
            'nome_arquivo': nome_arquivo,
            'tipo_arquivo': tipo_arquivo,
            'usuario_assinador': usuario_assinador,
            'arquivo_b64': arquivo_b64,
        })

print(dict_arquivos)
