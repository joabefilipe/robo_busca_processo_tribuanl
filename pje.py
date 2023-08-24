import requests
from config import *

json_login = {"username": username, "password": password, "grant_type": 'password', "client_id": 'petmais'}

session = requests.session()

url_host = 'https://homolog.peticionamais.com.br'
url_api = f'{url_host}/api'

url_auth = 'https://authhomolog.peticionamais.com.br/auth/realms/homologacao/protocol/openid-connect/token'
url_process = f'{url_api}/peticionamentos'
url_type_process = f'{url_api}/tipospeticao'
url_type_documents = f'{url_api}/documentos/intermediaria/tipos'

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

response_process = session.get(url_process, headers=headers, params=json_process)
response_process.raise_for_status()

response_petition = response_process.json().get('dados')[1]
tribunal = response_petition.get('tribunal').get('sigla')
sistema = response_petition.get('sistema').get('sigla')
instancia = response_petition.get('instancia').get('sigla')

params_petition_type = {'sistema': sistema, 'instancia': instancia, 'tipoIntermediaria': 'INTERMEDIARIA'}

response_petition_type = session.get(f'{url_type_process}/{tribunal}', headers=headers, params=params_petition_type)
response_petition_type.raise_for_status()

reponse_documents = response_petition_type.json()[0]
tipo_peticao = reponse_documents.get('nome')

params_documents_type = {'sistema': sistema, 'instancia': instancia, 'tipoIntermediaria': 'INTERMEDIARIA',
                         'tribunal': tribunal, 'tipo': 'e', 'nomeTipoPeticao': tipo_peticao}

response_documents_type = session.get(url_type_documents, headers=headers, params=params_documents_type)
response_documents_type.raise_for_status()
