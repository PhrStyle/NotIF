from flask import Blueprint, render_template, request, redirect, url_for, jsonify, send_file
from models.screens import Screens
from models.screenFiles import ScreenFiles, SideEnum, MediaTypeEnum
from models.files import Files
from db_init import SessionLocal
from services.instagramService import InstagramService
from services.fileUploadService import FileUploadService
from services.newsService import NewsService
from blueprints.auth_bp import login_required
import os

from services.screenFilesService import buscar_files_por_screen
import services.screenService as ScreenService

screens_bp = Blueprint('screens_bp', __name__, template_folder='../templates/screen')


@screens_bp.route('/vertelas')
@login_required
def ver_telas():
    telas = ScreenService.buscar_telas()
    return render_template("screen/index.html", telas=telas)

@screens_bp.route('/tela/<int:id_tela>')
def tela_exibicao(id_tela):
    session = SessionLocal()
    screen = session.query(Screens).get(id_tela)

    if not screen:
        session.close()
        return "Tela não encontrada", 404

    # Buscar notícias se a integração estiver ativa
    news_list = []
    if screen.news_integration:
        news_list = NewsService.get_ifmt_news()

    # Função para listar arquivos do Instagram
    def get_instagram_files():
        instagram_path = os.path.join('static', 'instagram')
        instagram_files = []

        if os.path.exists(instagram_path):
            for filename in os.listdir(instagram_path):
                file_path = os.path.join(instagram_path, filename)
                if os.path.isfile(file_path):
                    # Determinar se é vídeo baseado na extensão
                    is_video = filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.webm'))
                    instagram_files.append({
                        'file_name': filename,
                        'has_audio': False,  # Arquivos do Instagram nunca têm áudio
                        'is_video': is_video
                    })

        return instagram_files

    # Preparar dados dos arquivos do lado esquerdo
    if screen.instagram_left:
        left_files = get_instagram_files()
    else:
        left_files_query = session.query(ScreenFiles).filter(
            ScreenFiles.screen_id == id_tela,
            ScreenFiles.side == SideEnum.LEFT
        ).order_by(ScreenFiles.order_position).all()

        left_files = []
        for screen_file in left_files_query:
            if screen_file.files:
                left_files.append({
                    'file_name': screen_file.files.file_name,
                    'has_audio': screen_file.has_audio,
                    'is_video': screen_file.files.is_video
                })

    # Preparar dados dos arquivos do lado direito
    if screen.instagram_right:
        right_files = get_instagram_files()
    else:
        right_files_query = session.query(ScreenFiles).filter(
            ScreenFiles.screen_id == id_tela,
            ScreenFiles.side == SideEnum.RIGHT
        ).order_by(ScreenFiles.order_position).all()

        right_files = []
        for screen_file in right_files_query:
            if screen_file.files:
                right_files.append({
                    'file_name': screen_file.files.file_name,
                    'has_audio': screen_file.has_audio,
                    'is_video': screen_file.files.is_video
                })

    session.close()
    return render_template("screen/display.html",
                         screen=screen,
                         left_files=left_files,
                         right_files=right_files,
                         news_list=news_list)

@screens_bp.route('/editartela/<int:id_tela>', methods=['GET', 'POST'])
@login_required
def editar_tela(id_tela):
    session = SessionLocal()
    screen = session.query(Screens).get(id_tela)

    if not screen:
        session.close()
        return "Tela não encontrada", 404

    if request.method == 'POST':
        # Atualizar dados básicos da screen
        screen.name = request.form.get('name')
        screen.temRodape = bool(request.form.get('temRodape'))
        screen.footer_text = request.form.get('footer_text', '')
        screen.soundtrack = request.form.get('soundtrack', '')
        screen.instagram_left = bool(request.form.get('instagram_left'))
        screen.instagram_right = bool(request.form.get('instagram_right'))
        screen.news_integration = bool(request.form.get('news_integration'))

        # Limpar configurações antigas dos lados (somente se não for integração Instagram)
        session.query(ScreenFiles).filter(ScreenFiles.screen_id == id_tela).delete()

        # Processar lado esquerdo (somente se não for integração Instagram)
        if not screen.instagram_left:
            left_files = request.form.getlist('left_files[]')
            left_audio = request.form.getlist('left_audio[]')

            for idx, file_id in enumerate(left_files):
                if file_id:
                    audio_enabled = str(file_id) in left_audio
                    screen_file = ScreenFiles(
                        screen_id=id_tela,
                        file_id=int(file_id),
                        side=SideEnum.LEFT,
                        media_type=MediaTypeEnum.FILE,
                        has_audio=audio_enabled,
                        order_position=idx
                    )
                    session.add(screen_file)

        # Processar lado direito (somente se não for integração Instagram)
        if not screen.instagram_right:
            right_files = request.form.getlist('right_files[]')
            right_audio = request.form.getlist('right_audio[]')

            for idx, file_id in enumerate(right_files):
                if file_id:
                    audio_enabled = str(file_id) in right_audio
                    screen_file = ScreenFiles(
                        screen_id=id_tela,
                        file_id=int(file_id),
                        side=SideEnum.RIGHT,
                        media_type=MediaTypeEnum.FILE,
                        has_audio=audio_enabled,
                        order_position=idx
                    )
                    session.add(screen_file)

        session.commit()
        session.close()
        return redirect(url_for('screens_bp.ver_telas'))

    # Buscar arquivos disponíveis e configurações atuais
    available_files_query = session.query(Files).all()

    # Converter available_files para dicionários
    available_files = []
    for file in available_files_query:
        available_files.append({
            'id': file.id,
            'file_name': file.file_name,
            'file_path': file.file_path,
            'original_name': file.original_name,
            'is_video': file.is_video
        })

    left_config_query = session.query(ScreenFiles).filter(
        ScreenFiles.screen_id == id_tela,
        ScreenFiles.side == SideEnum.LEFT
    ).order_by(ScreenFiles.order_position).all()

    right_config_query = session.query(ScreenFiles).filter(
        ScreenFiles.screen_id == id_tela,
        ScreenFiles.side == SideEnum.RIGHT
    ).order_by(ScreenFiles.order_position).all()

    # Converter objetos ORM para dicionários
    left_config = []
    for config in left_config_query:
        config_dict = {
            'id': config.id,
            'file_id': config.file_id,
            'has_audio': config.has_audio,
            'order_position': config.order_position,
        }
        if config.files:
            config_dict['files'] = {
                'id': config.files.id,
                'file_name': config.files.file_name,
                'original_name': config.files.original_name,
                'is_video': config.files.is_video
            }
        left_config.append(config_dict)

    right_config = []
    for config in right_config_query:
        config_dict = {
            'id': config.id,
            'file_id': config.file_id,
            'has_audio': config.has_audio,
            'order_position': config.order_position,
        }
        if config.files:
            config_dict['files'] = {
                'id': config.files.id,
                'file_name': config.files.file_name,
                'original_name': config.files.original_name,
                'is_video': config.files.is_video
            }
        right_config.append(config_dict)

    session.close()
    return render_template('screen/edit.html',
                         screen=screen,
                         available_files=available_files,
                         left_config=left_config,
                         right_config=right_config)

@screens_bp.route('/api/upload', methods=['POST'])
@login_required
def upload_file():
    """API endpoint para upload de arquivos"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Nenhum arquivo enviado'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Nenhum arquivo selecionado'}), 400

        result = FileUploadService.save_file(file)
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Rotas para gerenciamento do banco de mídias

@screens_bp.route('/banco-midias')
@login_required
def banco_midias():
    """Tela de gerenciamento do banco de mídias"""
    session = SessionLocal()

    try:
        files = session.query(Files).all()

        # Converter para dicionários com informações do tipo de mídia
        medias = []
        for file in files:
            media_dict = {
                'id': file.id,
                'name': file.file_name,
                'original_name': file.original_name,
                'type': 'video' if file.is_video else 'image',
                'path': file.file_path
            }
            medias.append(media_dict)

        return render_template('screen/media_bank.html', medias=medias)

    finally:
        session.close()


@screens_bp.route('/upload-midias', methods=['POST'])
@login_required
def upload_midias():
    """Upload múltiplo de mídias"""
    session = SessionLocal()

    try:
        files = request.files.getlist('files')

        if not files or files[0].filename == '':
            return jsonify({'success': False, 'message': 'Nenhum arquivo enviado'})

        uploaded_count = 0
        errors = []

        for file in files:
            if file and file.filename:
                try:
                    result = FileUploadService.save_file(file)
                    if result['success']:
                        uploaded_count += 1
                    else:
                        errors.append(f"Erro ao enviar {file.filename}: {result.get('message', 'Erro desconhecido')}")
                except Exception as e:
                    errors.append(f"Erro ao processar {file.filename}: {str(e)}")

        if uploaded_count > 0:
            return jsonify({
                'success': True,
                'uploaded': uploaded_count,
                'errors': errors
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Nenhum arquivo foi enviado com sucesso',
                'errors': errors
            })

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        session.close()


@screens_bp.route('/delete-media/<int:media_id>', methods=['DELETE'])
@login_required
def delete_media(media_id):
    """Excluir uma mídia do banco"""
    session = SessionLocal()

    try:
        # Buscar o arquivo
        file = session.query(Files).get(media_id)

        if not file:
            return jsonify({'success': False, 'message': 'Mídia não encontrada'})

        # Verificar se a mídia está sendo usada em alguma tela
        screen_files = session.query(ScreenFiles).filter(ScreenFiles.file_id == media_id).all()

        if screen_files:
            screen_names = []
            for sf in screen_files:
                if sf.screen and sf.screen.name not in screen_names:
                    screen_names.append(sf.screen.name)

            return jsonify({
                'success': False,
                'message': f'Esta mídia está sendo usada nas telas: {", ".join(screen_names)}'
            })

        # Tentar remover o arquivo físico
        file_path = os.path.join('static', 'files', file.file_name)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Erro ao remover arquivo físico: {e}")

        # Remover do banco de dados
        session.delete(file)
        session.commit()

        return jsonify({'success': True, 'message': 'Mídia excluída com sucesso'})

    except Exception as e:
        session.rollback()
        return jsonify({'success': False, 'message': str(e)})
    finally:
        session.close()


@screens_bp.route('/download-media/<int:media_id>')
@login_required
def download_media(media_id):
    """Download de uma mídia"""
    session = SessionLocal()

    try:
        file = session.query(Files).get(media_id)

        if not file:
            return jsonify({'error': 'Mídia não encontrada'}), 404

        file_path = os.path.join('static', 'files', file.file_name)

        if not os.path.exists(file_path):
            return jsonify({'error': 'Arquivo não encontrado no sistema'}), 404

        return send_file(
            file_path,
            as_attachment=True,
            download_name=file.original_name or file.file_name
        )

    finally:
        session.close()


@screens_bp.route('/update-media-name/<int:media_id>', methods=['POST'])
@login_required
def update_media_name(media_id):
    """Atualizar o nome de uma mídia"""
    session = SessionLocal()

    try:
        data = request.get_json()
        new_name = data.get('newName')

        if not new_name or not new_name.strip():
            return jsonify({'success': False, 'message': 'Nome não pode estar vazio'})

        # Buscar o arquivo
        file = session.query(Files).get(media_id)

        if not file:
            return jsonify({'success': False, 'message': 'Mídia não encontrada'})

        # Atualizar o nome original
        file.original_name = new_name.strip()
        session.commit()

        return jsonify({'success': True, 'message': 'Nome atualizado com sucesso'})

    except Exception as e:
        session.rollback()
        return jsonify({'success': False, 'message': str(e)})
    finally:
        session.close()


@screens_bp.route('/criar-tela-vazia', methods=['POST'])
@login_required
def criar_tela_vazia():
    session = SessionLocal()

    try:
        # Gerar nome único para a nova tela
        base_name = "Nova Tela"
        counter = 1
        name = base_name

        # Verificar se já existe uma tela com esse nome
        while session.query(Screens).filter(Screens.name == name).first():
            counter += 1
            name = f"{base_name} {counter}"

        # Criar nova tela com nome único
        new_screen = Screens(
            name=name,
            temRodape=False,
            footer_text="",
            soundtrack=""
        )

        session.add(new_screen)
        session.commit()

        # Obter o ID da tela recém-criada
        screen_id = new_screen.id

        session.close()

        # Redirecionar para a tela de edição
        return redirect(url_for('screens_bp.editar_tela', id_tela=screen_id))

    except Exception as e:
        session.rollback()
        session.close()
        return f"Erro ao criar tela: {str(e)}", 500

@screens_bp.route('/api/instagram-files')
@login_required
def get_instagram_files():
    """API para listar arquivos do Instagram"""
    try:
        instagram_path = os.path.join('static', 'instagram')
        instagram_files = []
        
        if os.path.exists(instagram_path):
            for filename in os.listdir(instagram_path):
                file_path = os.path.join(instagram_path, filename)
                if os.path.isfile(file_path):
                    # Determinar se é vídeo baseado na extensão
                    is_video = filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.webm'))
                    instagram_files.append({
                        'file_name': filename,
                        'is_video': is_video
                    })
        
        return jsonify(instagram_files)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
