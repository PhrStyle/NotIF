from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from models.screens import Screens
from models.screenFiles import ScreenFiles, SideEnum, MediaTypeEnum
from models.files import Files
from db_init import SessionLocal
from services.instagramService import InstagramService
from services.fileUploadService import FileUploadService

from services.screenFilesService import buscar_files_por_screen
import services.screenService as ScreenService

screens_bp = Blueprint('screens_bp', __name__, template_folder='../templates/screen')


@screens_bp.route('/vertelas')
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

    # Buscar arquivos do lado esquerdo
    left_files_query = session.query(ScreenFiles).filter(
        ScreenFiles.screen_id == id_tela,
        ScreenFiles.side == SideEnum.LEFT
    ).order_by(ScreenFiles.order_position).all()

    # Buscar arquivos do lado direito
    right_files_query = session.query(ScreenFiles).filter(
        ScreenFiles.screen_id == id_tela,
        ScreenFiles.side == SideEnum.RIGHT
    ).order_by(ScreenFiles.order_position).all()

    # Preparar dados dos arquivos do lado esquerdo
    left_files = []
    for screen_file in left_files_query:
        if screen_file.files:
            left_files.append({
                'file_name': screen_file.files.file_name,
                'has_audio': screen_file.has_audio,
                'is_video': screen_file.files.is_video
            })

    # Preparar dados dos arquivos do lado direito
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
                         right_files=right_files)

@screens_bp.route('/editartela/<int:id_tela>', methods=['GET', 'POST'])
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

        # Limpar configurações antigas dos lados
        session.query(ScreenFiles).filter(ScreenFiles.screen_id == id_tela).delete()

        # Processar lado esquerdo
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

        # Processar lado direito
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
