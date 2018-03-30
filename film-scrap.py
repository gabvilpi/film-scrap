import urllib
import urllib.request
import urllib.error
import itertools
import re
from bs4 import BeautifulSoup
import pandas as pd

# definicion de funcion para bajar peliculas
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

# movielist contiene el orden alfabético que se recorrerá en la sección "Todas las películas" de filmaffinity
movielist = (
"0-9", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V",
"W", "X", "Y", "Z")

# testList es un listado de prueba
testList = ("X")
testList2 = ("X", "Y")

# Recorremos la sección de todas las películas según list e itertools.cout hasta llegar a una página que no existe

# inicializamos una lista para cada campo que queremos guardar
id_list = []
titulo_list = []



for i in testList:
    for num in itertools.count(1):
        url = "https://www.filmaffinity.com/es/allfilms_" + i + "_" + str(num) + ".html"
        page = download(url)
        if page is None:
            break
        else:
            # Extraemos los identificadores de pelicula de cada una de las páginas
            id = re.findall('data-movie-id="(.*?)"', str(page.read()))
            # Descargamos la página de cada película a partir de su identificador
            for j in id:
                movie = download("https://www.filmaffinity.com/es/film" + j + ".html")
                if page is not None:
                    # (PENDIENTE) Una vez descargada la página extraemos la información de la película
                    # print(movie.read())

                    # Parseamos el código HTML para navegar por las etiquetas
                    soup = BeautifulSoup(movie, 'html.parser')

                    # Vemos el código HTML correctamente
                    #fixed_html = soup.prettify()
                    #print(fixed_html)

                    # Buscamos entre las etiquetas dl la que tenga la clase movie-info
                    dl = soup.find('dl', attrs={'class': 'movie-info'})

                    # Vemos solo la parte de movie-info
                    # print(dl)

                     # Seleccionamos el primer elemento dd
                    dd = dl.find('dd')
                    titulo = dd.text.strip()

                    # quitamos 'aka' en los casos en los que existe en el titulo
                    if titulo[-3:] == 'aka': titulo = titulo[:-3].strip()

                    print('id: %d , titulo: %s' % (int(j), titulo))
                    type(j)
                    
                    # añadimos a cada una de las listas el dato correspondiente a la ultima pelicula
                    id_list.append(int(j))
                    titulo_list.append(titulo)
                   
# creamos una dataframe con  todas las listas
df = pd.DataFrame({'id' : id_list, 'titulo': titulo_list }) 

# guardamos la dataframe a disco
df.to_csv('filmaffinity.csv', encoding='utf-8')   


                    
