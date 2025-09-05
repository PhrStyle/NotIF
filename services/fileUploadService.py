import os
import uuid
from werkzeug.utils import secure_filename
from models.files import Files
from db_init import SessionLocal

class FileUploadService:
    
    UPLOAD_FOLDER = '/home/phrstyle/dev/NotIF/static/files'
    ALLOWED_EXTENSIONS = {'mp4', 'webm', 'ogg', 'avi', 'mov', 'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'}
    VIDEO_EXTENSIONS = {'mp4', 'webm', 'ogg', 'avi', 'mov'}
    
    @staticmethod
    def allowed_file(filename):
        """Verifica se o arquivo tem uma extensão permitida"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in FileUploadService.ALLOWED_EXTENSIONS
    
    @staticmethod
    def is_video(filename):
        """Verifica se o arquivo é um vídeo"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in FileUploadService.VIDEO_EXTENSIONS
    
    @staticmethod
    def generate_unique_filename(original_filename):
        """Gera um nome único para o arquivo para evitar duplicatas"""
        extension = original_filename.rsplit('.', 1)[1].lower()
        unique_name = f"{uuid.uuid4().hex}.{extension}"
        return unique_name
    
    @staticmethod
    def save_file(file):
        """
        Salva o arquivo no sistema de arquivos e registra no banco de dados
        
        Args:
            file: Arquivo enviado via upload
            
        Returns:
            dict: Resultado da operação com sucesso/erro e dados do arquivo
        """
        try:
            if not file or file.filename == '':
                return {'success': False, 'error': 'Nenhum arquivo selecionado'}
            
            if not FileUploadService.allowed_file(file.filename):
                return {'success': False, 'error': 'Tipo de arquivo não permitido'}
            
            # Gerar nome único
            original_filename = secure_filename(file.filename)
            unique_filename = FileUploadService.generate_unique_filename(original_filename)
            
            # Garantir que o diretório existe
            os.makedirs(FileUploadService.UPLOAD_FOLDER, exist_ok=True)
            
            # Verificar se o nome do arquivo já existe no banco
            session = SessionLocal()
            existing_file = session.query(Files).filter_by(file_name=unique_filename).first()
            if existing_file:
                session.close()
                return {'success': False, 'error': 'Nome de arquivo duplicado'}
            
            # Caminho completo do arquivo
            file_path = os.path.join(FileUploadService.UPLOAD_FOLDER, unique_filename)
            
            # Salvar arquivo no sistema de arquivos
            file.save(file_path)
            
            # Registrar no banco de dados
            new_file = Files(
                file_name=unique_filename,
                file_path=file_path,
                is_video=FileUploadService.is_video(original_filename),
                original_name=original_filename
            )
            
            session.add(new_file)
            session.commit()
            
            # Converter para dicionário para retorno
            file_dict = {
                'id': new_file.id,
                'file_name': new_file.file_name,
                'file_path': new_file.file_path,
                'is_video': new_file.is_video,
                'original_name': new_file.original_name
            }
            
            session.close()
            
            return {
                'success': True,
                'message': 'Arquivo salvo com sucesso',
                'file': file_dict
            }
            
        except Exception as e:
            if 'session' in locals():
                session.rollback()
                session.close()
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def delete_file(file_id):
        """
        Remove um arquivo do sistema de arquivos e do banco de dados
        
        Args:
            file_id: ID do arquivo no banco de dados
            
        Returns:
            dict: Resultado da operação
        """
        session = SessionLocal()
        try:
            file_record = session.query(Files).get(file_id)
            if not file_record:
                return {'success': False, 'error': 'Arquivo não encontrado'}
            
            # Remover arquivo físico
            file_path = os.path.join(FileUploadService.UPLOAD_FOLDER, file_record.file_name)
            if os.path.exists(file_path):
                os.remove(file_path)
            
            # Remover do banco
            session.delete(file_record)
            session.commit()
            
            return {'success': True, 'message': 'Arquivo removido com sucesso'}
            
        except Exception as e:
            session.rollback()
            return {'success': False, 'error': f'Erro ao remover arquivo: {str(e)}'}
        finally:
            session.close()
    
    @staticmethod
    def get_all_files():
        """Retorna todos os arquivos registrados"""
        session = SessionLocal()
        try:
            files = session.query(Files).all()
            return [{
                'id': f.id,
                'file_name': f.file_name,
                'file_path': f.file_path,
                'original_name': f.original_name,
                'is_video': f.is_video
            } for f in files]
        finally:
            session.close()
