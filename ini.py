import requests
import base64
import logging
from datetime import datetime, timedelta

# Configuração básica
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CSLOGAPI:
    def __init__(self):
        self.base_url = ""
        self.auth = ("login", "senha")
        self.token = None
        self.token_expiration = None

    def _get_auth_header(self):
        """Cria header de autenticação Basic Auth"""
        auth_str = f"{self.auth[0]}:{self.auth[1]}"
        return {'Authorization': f'Basic {base64.b64encode(auth_str.encode()).decode()}'}

    def test_connection(self):
        """Testa se a API está respondendo"""
        try:
            response = requests.get(
                self.base_url,
                headers=self._get_auth_header(),
                timeout=10
            )
            logger.info(f"Teste de conexão - Status: {response.status_code}")
            logger.info(f"Resposta: {response.text[:200]}...")  # Log parcial
            return response.status_code in [200, 401, 403]  # Se retornar algo, mesmo que não autorizado
        except Exception as e:
            logger.error(f"Falha no teste de conexão: {str(e)}")
            return False

    def get_token(self):
        """Obtém token de acesso com tratamento robusto"""
        if self.token and self.token_expiration and datetime.now() < self.token_expiration:
            return self.token

        endpoint = f"{self.base_url}/getToken"
        params = {'login': self.auth[0]}  # Usando o usuário 'carga' como login

        try:
            response = requests.get(
                endpoint,
                headers=self._get_auth_header(),
                params=params,
                timeout=15
            )

            logger.info(f"Resposta bruta do servidor: {response.status_code} - {response.text}")

            # Tratamento especial para respostas vazias ou não-JSON
            if not response.text.strip():
                raise ValueError("Resposta vazia do servidor")

            try:
                data = response.json()
            except ValueError:
                raise ValueError(f"Resposta não é JSON válido: {response.text}")

            if response.status_code != 200:
                error_msg = data.get('erro', f"Erro HTTP {response.status_code}")
                raise ValueError(error_msg)

            if 'token' not in data:
                raise ValueError("Resposta não contém token")

            self.token = data['token']
            self.token_expiration = datetime.now() + timedelta(hours=24)
            logger.info(f"Token obtido com sucesso (expira em: {self.token_expiration})")
            return self.token

        except Exception as e:
            logger.error(f"Falha ao obter token: {str(e)}")
            raise Exception(f"Não foi possível obter token: {str(e)}")

# Teste manual
if __name__ == "__main__":
    api = CSLOGAPI()
    
    print("=== Teste de Conexão ===")
    if api.test_connection():
        print("✅ Conexão com a API estabelecida")
        
        print("\n=== Teste de Obtenção de Token ===")
        try:
            token = api.get_token()
            print(f"✅ Token obtido: {token}")
        except Exception as e:
            print(f"❌ Falha: {str(e)}")
            print("\nPossíveis causas:")
            print("- Endpoint /getToken não existe")
            print("- Credenciais incorretas")
            print("- IP não está liberado no servidor")
            print("- Problema na configuração da API")
    else:
        print("❌ Falha ao conectar na API")
        print("Verifique:")
        print("- URL da API está correta?")
        print("- Servidor está online?")
        print("- Rede/firewall permite a conexão?")
