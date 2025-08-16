import requests
import json
from typing import List, Dict, Optional

class InstagramService:
    """
    Serviço para integração com Instagram.
    Por enquanto, retorna dados simulados. Para implementação real,
    seria necessário usar a Instagram Basic Display API ou Graph API.
    """
    
    @staticmethod
    def get_user_media(username: str, limit: int = 10) -> List[Dict]:
        """
        Busca mídia de um usuário do Instagram.
        
        Args:
            username: Nome do usuário (sem @)
            limit: Número máximo de posts para retornar
            
        Returns:
            Lista de dicionários com informações da mídia
        """
        # Por enquanto, retorna dados simulados
        # Em uma implementação real, aqui faria chamadas para a API do Instagram
        
        mock_data = [
            {
                'id': f'{username}_1',
                'media_type': 'IMAGE',
                'media_url': f'https://via.placeholder.com/800x600?text={username}+Post+1',
                'caption': f'Post 1 de @{username}',
                'timestamp': '2024-01-15T10:30:00Z'
            },
            {
                'id': f'{username}_2',
                'media_type': 'VIDEO',
                'media_url': f'https://sample-videos.com/zip/10/mp4/480/SampleVideo_480x270_1mb.mp4',
                'thumbnail_url': f'https://via.placeholder.com/800x600?text={username}+Video+2',
                'caption': f'Vídeo de @{username}',
                'timestamp': '2024-01-14T15:45:00Z'
            },
            {
                'id': f'{username}_3',
                'media_type': 'IMAGE',
                'media_url': f'https://via.placeholder.com/800x600?text={username}+Post+3',
                'caption': f'Outro post de @{username}',
                'timestamp': '2024-01-13T09:20:00Z'
            }
        ]
        
        return mock_data[:limit]
    
    @staticmethod
    def get_user_info(username: str) -> Optional[Dict]:
        """
        Busca informações básicas do usuário.
        
        Args:
            username: Nome do usuário (sem @)
            
        Returns:
            Dicionário com informações do usuário ou None se não encontrado
        """
        # Dados simulados
        return {
            'username': username,
            'full_name': f'{username.title()} Profile',
            'profile_picture_url': f'https://via.placeholder.com/150x150?text={username[0].upper()}',
            'followers_count': 1234,
            'media_count': 567
        }
    
    @staticmethod
    def validate_username(username: str) -> bool:
        """
        Valida se um nome de usuário é válido.
        
        Args:
            username: Nome do usuário para validar
            
        Returns:
            True se válido, False caso contrário
        """
        if not username:
            return False
            
        # Remove @ se presente
        username = username.lstrip('@')
        
        # Validações básicas do Instagram
        if len(username) < 1 or len(username) > 30:
            return False
            
        # Apenas letras, números, pontos e underscores
        allowed_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._')
        if not all(c in allowed_chars for c in username):
            return False
            
        return True
