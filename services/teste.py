import pathlib
from datetime import datetime, timedelta

from instaloader import Instaloader, Profile

data_inicio = datetime.today() - timedelta(days=6)
L=Instaloader()
PROFILE = 'ifmtcbaemprego'
profile = Profile.from_username(L.context, PROFILE)
post_sorted = sorted(profile.get_posts(),key=lambda post: post.likes, reverse=True)
for post in post_sorted:
    #Faz o download das publicações que estão dentro do prazo estabelecido e as que estão fixadas
    if post.date >= data_inicio or post.is_pinned:
        L.download_post(post, pathlib.Path('ifmtcbaemprego'))
#Chama a função de correção da pasta com os arquivos do Instagram