import requests
import re

from lxml import html


usuario = ''
senha = ''

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/113.0.0.0 Safari/537.36'
}

session = requests.session()

url_login = 'https://esaj.tjsp.jus.br/sajcas/login?'
url_host = 'https://esaj.tjsp.jus.br'
url_pet = 'https://esaj.tjsp.jus.br/petpg/'

url_pet_api = f'{url_pet}/api'
url_aux = f'{url_host}/tarefas-adv/'
url_api = f'{url_aux}api'

url_peticionante = f'{url_pet_api}/peticionantes'
url_consulta = f'{url_pet}/peticoes/consulta'
url_peticao = f'{url_pet_api}/peticoes'
url_menu = f'{url_api}/menu'
url_usuario = f'{url_api}/usuario'

params_login = {'service': f'{url_host}/esaj/j_spring_cas_security_check'}

response_pagina_tribunal = session.get(url=url_login, params=params_login, headers=headers)
response_pagina_tribunal.raise_for_status()
root = html.fromstring(response_pagina_tribunal.text)

execution = root.xpath('//*[@id="flowExecutionKey"]')[0].attrib.get('value')

esaj_login = {'username': usuario, 'password': senha, 'lt': '', 'execution': execution, '_eventId': 'submit',
              'pbEntrar': 'Entrar', 'signature': '', 'certificadoSelecionado': '', 'certificado': ''}

response_login = session.post(url=url_login, data=esaj_login, headers=headers,
                              allow_redirects=True)
response_login.raise_for_status()

response_tarefa = session.get(url_aux, headers=headers)

response_tarefa_adv = session.get(url=url_menu, headers=headers)

response_usuario = session.get(url=url_usuario, headers=headers)
response_usuario.raise_for_status()

response_peticionante = session.get(url=url_peticionante, headers=headers)
response_peticionante.raise_for_status()
peticionante = response_peticionante.json()[0]
cd_perfil = peticionante.get('cdPerfil')
cd_usuario = peticionante.get('cdUsuario')
nm_usuario = peticionante.get('nmUsuario')
nm_perfil = peticionante.get('nmPerfil')
id_usuario = f'{cd_perfil}-{cd_usuario}-{cd_usuario}'
search = f'{nm_usuario} {nm_usuario} {nm_perfil}'.lower()

peticionante.update({
    'id': id_usuario,
    'search': search,
})

response_query_process = session.get(url=url_consulta, headers=headers)
response_query_process.raise_for_status()

numero_processo = ''
response_process = {'cadastrante': None, 'instancias': ["PG"], 'limit': '30', 'numeroProcesso': numero_processo,
                    'offset': '0', 'pagina': '1', 'periodoUltimaAtualizacaoFim': None,
                    'periodoUltimaAtualizacaoInicio': None, 'peticionante': peticionante, 'situacoes': [1],
                    'tiposPeticao': [1, 2]}


headers_processo = headers.copy()
headers_processo.update({
    'Content-Type': 'application/json;charset=UTF-8'
})

response_search_process = session.post(url=url_peticao, headers=headers_processo,
                                       json=response_process)
response_search_process.raise_for_status()

url_consulta_processo = response_search_process.json()['resumoPeticao'][0]['urlConsultaProcesso']
response_url = session.get(url=url_consulta_processo, headers=headers)
response_url.raise_for_status()

root_principal = html.fromstring(response_url.text)
trs_movimentacoes = root_principal.xpath('//*[@id="tabelaTodasMovimentacoes"]/tr')
erros = root_principal.xpath('//*[@id="mensagemRetorno"]/li/text()')
if erros:
    raise Exception(erros[0])

dict_movimentacoes = []
for tr in trs_movimentacoes:
    data_movimentacao = tr.xpath('./td/text()')[0].strip()
    descricao = tr.xpath('./td/text()')[2].strip()

    if descricao == '':
        descricao = root_principal.xpath('//*[@id="tabelaTodasMovimentacoes"]/tr/td/a/text()')[2].strip()

    dict_movimentacoes.append({
        'data': data_movimentacao,
        'descrição': descricao,
    })

dict_dados_processo = {}
classe = root_principal.xpath('//*[@id="classeProcesso"]/text()')[0]
assunto = root_principal.xpath('//*[@id="assuntoProcesso"]/text()')[0]
foro = root_principal.xpath('//*[@id="foroProcesso"]/text()')[0]
vara = root_principal.xpath('//*[@id="varaProcesso"]/text()')[0]
area = root_principal.xpath('//*[@id="areaProcesso"]/span/text()')[0]
valor_acao = root_principal.xpath('//*[@id="valorAcaoProcesso"]/text()')[0]

dict_dados_processo.update({
    'classe': classe,
    'assunto': assunto,
    'foro': foro,
    'vara': vara,
    'area': area,
    'valor': valor_acao,
})

principais_partes = root_principal.xpath('//*[@id="tablePartesPrincipais"]/tr')
dict_partes = []
for tr in principais_partes:
    nomes_partes = [c.strip() for c in tr.xpath('./td/text()') if c.strip()]
    if len(tr.xpath('./td/span/text()')) > 1:
        advogado = tr.xpath('./td/span/text()')[1].strip()
        nome_advogado = f'{advogado}{nomes_partes[1]}'

    dict_partes.append({
        'tipo_parte':  tr.xpath('./td/span/text()')[0].strip(),
        'tipo_advogado': nome_advogado,
        'nome_parte': nomes_partes[0],
    })

print(dict_partes)





