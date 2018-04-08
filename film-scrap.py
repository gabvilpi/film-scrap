import urllib
import urllib.request
import urllib.error
import itertools
import re
from bs4 import BeautifulSoup
import pandas as pd


# inicializacion

movies_id = 0
new_movies_id = 0
df = 0
new_df = 0

def download(url, user_agent="gabvilpi", num_retries=2):
    headers = {'User-agent': user_agent}
    request = urllib.request.Request(url=url, headers=headers)
    print("Downloading:", url)
    try:
        html = urllib.request.urlopen(request)
# HACE FALTA UNA INSTRUCCION QUE PARE EL DOWNLOAD SI SOBREPASAMOS EL LIMITE. HE INTENTADO ESTO PERO NO FUNCIONA
#        if '<title>Too many request</title>' in str(html.read()): 
#            return None
#            print('Too many downloads. Try later')
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

        # extraemos país
        span = soup.find('span', attrs={'id': 'country-img'})
        img = span.find_all('img')[0]['alt']
        if img != None:
            pais = img
            #print(pais)
        else:
            pais = 'NA'


       # extraemos sinopsis
        dl = soup.find('dd', attrs={'itemprop': 'description'})
        if dl != None:
            sinopsis = dl.text.strip()
        else:
            sinopsis = 'NA'

        
        # añadimos a cada una de las listas el dato correspondiente a la ultima pelicula
        id_list.append(int(j))
        titulo_list.append(titulo)
        año_list.append(año)
        duracion_list.append(duracion)
        pais_list.append(pais)
        sinopsis_list.append(sinopsis)
        web_list.append(movie_url)

def saveData(id_list, titulo_list, año_list, duracion_list, pais_list, sinopsis_list,web_list):

    if os.path.exists('filmaffinity.csv'): 
#        print('filmaffinity exists')
        df = pd.read_csv('filmaffinity.csv')
    else:
#        print('filmaffinity does not exist')
        df = pd.DataFrame({'id': [],
                           'titulo': [],
                           'año': [],
                           'duracion (min)': [],
                           'pais': [],
                           'sinopsis': [],
                           'web': [],
                           },
                          columns=['id', 'titulo', 'año', 'duracion (min)', 'pais', 'sinopsis', 'web'])

        
    # creamos una dataframe con  todas las listas
    new_df = pd.DataFrame({'id': id_list,
                           'titulo': titulo_list,
                           'año': año_list,
                           'duracion (min)': duracion_list,
                           'pais': pais_list,
                           'sinopsis': sinopsis_list,
                           'web': web_list,
                           },
                          columns=['id', 'titulo', 'año', 'duracion (min)', 'pais', 'sinopsis', 'web'])

    
    df = df.append(new_df)
    
    # guardamos la dataframe a disco
    df.to_csv('filmaffinity.csv', index = False , encoding='utf-8')
    movies_id.to_csv('movies_id.csv', index = False, encoding = 'utf-8')


# movielist contiene el orden alfabético que se recorrerá en la sección "Todas las películas" de filmaffinity
movielist = (
"0-9", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V",
"W", "X", "Y", "Z")

# testList es un listado de prueba
testList = ("X")
testList2 = ("Z")

# Contador de peliculas descargadas
contador = 0

# stop para el bucle principal cuando ha habido un error en el scrap
stop = False

# inicializamos una lista para cada campo que queremos guardar
id_list = []
titulo_list = []
año_list = []
duracion_list = []
pais_list = []
sinopsis_list = []
web_list = []

# bucle para descargar las ids de todo filmaffinity
if os.path.exists('movies_id.csv'): 
#    print('movies_id exists')
    movies_id = pd.read_csv('movies_id.csv')
else:
#    print('movies_id does not exist')
    movies_id = pd.DataFrame({'id':[],'downloaded':[]}, columns = ['id', 'downloaded'])
    
ident_list = []

for i in testList2:
    for num in itertools.count(1):
        url = "https://www.filmaffinity.com/es/allfilms_" + i + "_" + str(num) + ".html"
        page = download(url)
        if page is None or stop:
            break
        else:
            # Extraemos los identificadores de pelicula de cada una de las páginas
            id = re.findall('data-movie-id="(.*?)"', str(page.read()))
            for j in id:
                if int(j) not in list(movies_id['id']): 
                    ident_list.append(j)
                    
downloaded_list = [0]*len(ident_list)                    
new_movies_id = pd.DataFrame({'id':ident_list, 'downloaded':downloaded_list}, columns=['id', 'downloaded'])                

movies_id = movies_id.append(new_movies_id)

#movies_id.to_csv('movies_id.csv', index = False, encoding='utf-8')

# Descargamos la página de cada película a partir de su identificador
for j in movies_id.loc[movies_id['downloaded']==0, 'id']:
    movie_url = "https://www.filmaffinity.com/es/film" + str(int(j)) + ".html"
    movie = download(movie_url)
    if movie is not None:
        # Realizamos scrap de la web de la película. Si la función devuelve True paramos el bucle (Too many requests?)
        if scrap(movie):
            stop = True
            break
        # incrementamos el contador de películas descargadas
        contador += 1
        movies_id.loc[movies_id['id']==j, 'downloaded'] = int(1)

# Finalmente almacenamos los datos en Disco
saveData(id_list, titulo_list, año_list, duracion_list, pais_list,sinopsis_list, web_list)
print('Finished')
