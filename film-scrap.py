import urllib
import urllib.request
import urllib.error
import itertools
import re
from bs4 import BeautifulSoup

'''
La función download descarga una web indicando el nombre del agente y el número de reintentos.
Se realiza un tratamiento de las excepciones para mostrar el error o reintentar la descarga si el error es de tipo 5XX
'''
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
                return download(url, user_agent, num_retries-1)
    return html

# list contiene el orden alfabético que se recorrerá en la sección "Todas las películas" de filmaffinity
list = ("0-9", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z")
# testList es un listado de prueba
testList = ("X")
# Recorremos la sección de todas las películas según list e itertools.cout hasta llegar a una página que no existe
for i in testList:
    for num in itertools.count(1):
        url="https://www.filmaffinity.com/es/allfilms_" + i + "_" + str(num) + ".html"
        page = download(url)
        if page is None:
            break
        else:
            # Extraemos los identificadores de pelicula de cada una de las páginas
            id = re.findall('data-movie-id="(.*?)"', str(page.read()))
            # Descargamos la página de cada película a partir de su identificador
            for j in id:
                movie = download("https://www.filmaffinity.com/es/film" + str(j) + ".html")
                if page is not None:
                    # (PENDIENTE) Una vez descargada la página extraemos la información de la película
                     #print(movie.read())

                    # Parseamos el código HTML para navegar por las etiquetas
                    soup = BeautifulSoup(movie, 'html.parser')

                    # Vemos el código HTML correctamente 
                    #fixed_html = soup.prettify()
                    #print(fixed_html)
                    
                    # Buscamos entre las etiquetas dl la que tenga la clase movie-info
                    dl = soup.find('dl', attrs={'class':'movie-info'})

                    # Vemos solo la parte de movie-info
                    # print(dl)

                    #Seleccionamos el primer elemento dd
                    dd = dl.find('dd')
                    titulo = dd.text
                    print(titulo)
