import urllib
import urllib.request
import urllib.error
import itertools
import re
from bs4 import BeautifulSoup
import pandas as pd

# definición de función para bajar peliculas
def download(url, user_agent="gabvilpi", num_retries=2):
    print("Downloading:", url)
    headers = {'User-agent': user_agent}
    request = urllib.request.Request(url=url, headers=headers)
    try:
        html = urllib.request.urlopen(request)
    except urllib.error.URLError as e:
        print("Download error:", e.reason)
        html = None
        if num_retries > 0:
            if hasattr(e, 'code') and 500 <= e.code < 600:
                # Reintento para errores HTTP 5XX
                return download(url, user_agent, num_retries - 1)
    return html

# definición de función para realizar scrap
def scrap(movie):
    # (PENDIENTE) Una vez descargada la página extraemos la información de la película
    # print(movie.read())

    # Parseamos el código HTML para navegar por las etiquetas
    soup = BeautifulSoup(movie, 'html.parser')

    # Vemos el código HTML correctamente
    # fixed_html = soup.prettify()
    # print(fixed_html)

    # extraemos nombre
    # Buscamos entre las etiquetas dl la que tenga la clase movie-info
    dl = soup.find('dl', attrs={'class': 'movie-info'})

    if dl is None:
        # Paramos. No se encuentra movie-info, posible 'Too many requests'
        return True
    else:
        # Vemos solo la parte de movie-info
        # print(dl)

        # Seleccionamos el primer elemento dd
        dd = dl.find('dd')
        titulo = dd.text.strip()

        # quitamos 'aka' en los casos en los que existe en el titulo
        if titulo[-3:] == 'aka': titulo = titulo[:-3].strip()

        # print('id: %d , titulo: %s' % (int(j), titulo))

        # extraemos año
        dl = soup.find('dd', attrs={'itemprop': 'datePublished'})
        año = int(dl.text.strip())

        # extraemos duracion
        dl = soup.find('dd', attrs={'itemprop': 'duration'})
        if dl != None:
            duracion = dl.text.strip().split()[0]
        else:
            duracion = 'NA'

        # añadimos a cada una de las listas el dato correspondiente a la ultima pelicula
        id_list.append(int(j))
        titulo_list.append(titulo)
        año_list.append(año)
        duracion_list.append(duracion)
        web_list.append(movie_url)

def saveData(id_list, titulo_list, año_list, duracion_list, web_list):
    # creamos una dataframe con  todas las listas
    df = pd.DataFrame({'id': id_list,
                       'titulo': titulo_list,
                       'año': año_list,
                       'duracion (min)': duracion_list,
                       'web': web_list,
                       },
                      columns=['id', 'titulo', 'año', 'duracion (min)', 'web'])

    # guardamos la dataframe a disco
    df.to_csv('filmaffinity.csv', encoding='utf-8')

    df.head()

# movielist contiene el orden alfabético que se recorrerá en la sección "Todas las películas" de filmaffinity
movielist = (
"0-9", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V",
"W", "X", "Y", "Z")

# testList es un listado de prueba
testList = ("X")
testList2 = ("X", "Y")

# Contador de peliculas descargadas
contador = 0

# stop para el bucle principal cuando ha habido un error en el scrap
stop = False

# inicializamos una lista para cada campo que queremos guardar
id_list = []
titulo_list = []
año_list = []
duracion_list = []
web_list = []

# Bucle principal: Recorremos la sección de todas las películas según list e itertools.cout hasta llegar a una página que no existe
for i in testList:
    for num in itertools.count(1):
        url = "https://www.filmaffinity.com/es/allfilms_" + i + "_" + str(num) + ".html"
        page = download(url)
        if page is None or stop:
            break
        else:
            # Extraemos los identificadores de pelicula de cada una de las páginas
            id = re.findall('data-movie-id="(.*?)"', str(page.read()))
            # Descargamos la página de cada película a partir de su identificador
            for j in id:
                movie_url = "https://www.filmaffinity.com/es/film" + j + ".html"
                movie = download(movie_url)
                if movie is not None:
                    # Realizamos scrap de la web de la película. Si la función devuelve True paramos el bucle (Too many requests?)
                    if scrap(movie):
                        stop = True
                        break
                    # incrementamos el contador de películas descargadas
                    contador += 1

# Finalmente almacenamos los datos en Disco
saveData(id_list, titulo_list, año_list, duracion_list, web_list)

print(contador)