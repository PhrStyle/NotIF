import requests
from bs4 import BeautifulSoup
import logging

class NewsService:
    @staticmethod
    def get_ifmt_news():
        """
        Busca as últimas 5 notícias do site do IFMT CBA
        Retorna uma lista com os títulos das notícias
        """
        try:
            lista_noticias = []
            
            # URL da página de notícias do IFMT a ser requisitada
            response = requests.get('https://cba.ifmt.edu.br/conteudo/noticias/', timeout=10)
            response.raise_for_status()  # Levanta exceção se houver erro HTTP
            
            content = response.content
            
            # Faz a busca através das tags HTML da página
            site = BeautifulSoup(content, 'html.parser')
            noticias = site.findAll('div', attrs={'class': 'small-12 columns borda-esquerda'})
            
            for noticia in noticias:
                titulo = noticia.find('p', attrs={'class': 'no-margin espacamento-medio'})
                if titulo and titulo.text:
                    # Cria uma lista com todos os títulos das notícias encontrados
                    lista_noticias.append(titulo.text.strip())
                
                # Limitar a 5 notícias
                if len(lista_noticias) >= 5:
                    break
            
            return lista_noticias
            
        except requests.exceptions.RequestException as e:
            logging.error(f"Erro ao buscar notícias do IFMT: {e}")
            return ["Erro ao carregar notícias do IFMT"]
        except Exception as e:
            logging.error(f"Erro inesperado ao processar notícias: {e}")
            return ["Erro ao processar notícias"]
