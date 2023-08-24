import requests
from config import *

json_login = {"username": username, "password": password, "grant_type": 'password', "client_id": 'petmais'}

session = requests.session()

url_host = 'https://homolog.peticionamais.com.br'
url_api = f'{url_host}/api'

url_auth = 'https://authhomolog.peticionamais.com.br/auth/realms/homologacao/protocol/openid-connect/token'
url_process = f'{url_api}/peticionamentos'
url_type_category = f'{url_api}/tipospeticao'
url_type = f'{url_api}/categorias'
url_type_documents = f'{url_api}/documentos/intermediaria/tipos'
url_type_participation = f'{url_api}/envolvimentos/intermediaria'

response_login = session.post(url=url_auth, data=json_login, headers=headers)
response_login.raise_for_status()

response_data = response_login.json()
token = response_data.get('access_token')

numero_processo = ''

json_process = {'pagina': '1', 'total': '10', 'tipo': '2,1', 'status': 'ATIVO', 'oculto': 'false',
                'suportado': 'true', 'numero': numero_processo}

headers.update({
    'Authorization': f'Bearer {token}',
})

response_process = session.get(url=url_process, headers=headers, params=json_process)
response_process.raise_for_status()

response_petition = response_process.json().get('dados')[0]
tribunal = response_petition.get('tribunal').get('sigla')
instancia = response_petition.get('instancia').get('sigla')
sistema = response_petition.get('sistema').get('sigla')

params_type_category = {'instancia': instancia, 'tipoIntermediaria': 'INTERMEDIARIA', 'sistema': sistema}

response_type_category = session.get(url=f'{url_type_category}/{tribunal}', headers=headers,
                                     params=params_type_category)
response_type_category.raise_for_status()

response_category = response_type_category.json()[1]
area = response_category.get('area')
tipo = response_category.get('tipo')

params_category = {'siglaTribunal': tribunal, 'instancia': instancia, 'sistema': sistema}

response_name_category = session.get(url=url_type, headers=headers, params=params_category)

c = None
for nome_categoria in response_name_category.json():
    if nome_categoria.get('nome') == 'Petições Diversas':
        c = nome_categoria.get('nome')
        break

params_type_petition = {'area': area, 'tipo': tipo, 'nomeCategoria': c, 'tribunal': tribunal,
                        'instancia': instancia, 'tipoIntermediaria': 'INTERMEDIARIA', 'sistema': sistema}

response_type_petition = session.get(url=url_type_category, headers=headers, params=params_type_petition)
response_type_petition.raise_for_status()
nome_tipo_peticao = response_type_petition.json()[4].get('nome')

params_type_documents = {'sistema': sistema, 'area': area, 'tipo': tipo, 'nomeTipoPeticao': nome_tipo_peticao,
                         'tribunal': tribunal, 'instancia': instancia, 'tipoIntermediaria': 'INTERMEDIARIA'}

response_typo_documents = session.get(url=url_type_documents, headers=headers, params=params_type_documents)
response_typo_documents.raise_for_status()

params_type_participation = {'tribunal': tribunal, 'instancia': instancia,
                             'nomeTipoPeticao': nome_tipo_peticao, 'parte': 'PARTE_ATIVA', 'sistema': sistema,
                             'tipo': tipo, 'area': area}

response_type_participation = session.get(url=url_type_participation, headers=headers, params=params_type_participation)
tipo_ativo = response_type_participation.json()[0].get('nome')
response_type_participation.raise_for_status()

params_type_participation = {'tribunal': tribunal, 'instancia': instancia,
                             'nomeTipoPeticao': nome_tipo_peticao, 'parte': 'PARTE_PASSIVA', 'sistema': sistema,
                             'tipo': tipo, 'area': area}

response_type_participation = session.get(url=url_type_participation, headers=headers, params=params_type_participation)
tipo_passivo = response_type_participation.json()[0].get('nome')
response_type_participation.raise_for_status()



