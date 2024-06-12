import os
import psycopg2
from dotenv import load_dotenv # type: ignore
import requests


load_dotenv()

def connect_db():
  connection = psycopg2.connect(
    database=os.getenv('DB_NAME'), 
    user=os.getenv('DB_USER'), 
    password=os.getenv('DB_PASS'), 
    host=os.getenv('DB_HOST'), 
    port=5432)
  
  return connection

def image_getter(username):
  connection = connect_db()
  cursor = connection.cursor()


  # Ejecutar la consulta usando marcadores de posición
  query = '''
SELECT u."id", u."name", od."fileName", od."objectKey"
FROM users u
JOIN official_documents od ON u.id = od."userId"
WHERE u."name" = %s
AND (od."fileName" LIKE '%%png%%' OR od."fileName" LIKE '%%jpeg%%' OR od."fileName" LIKE '%%jpg%%');
'''
  # Ejecutar la consulta con el parámetro
  cursor.execute(query, (username,))
  # Guardamos las filas obtenidas
  record = cursor.fetchall()
  objectKey = record[0][3]

  if len(record) == 1:
    print(f'objectKey: {objectKey}')
    convert_image_from_url(objectKey)
  else:
    print('Hay más de un elemento')


  # Cerramos las conexiones con la DB
  cursor.close()
  connection.close()

def convert_image_from_url(objectKey):
  HEADERS = { 
    "X-Api-Key":os.getenv('API_KEY')
  }
  BODY = {
    "fileUrl": objectKey,
    "bucketName": "hybed-docs-files-prod"
  }
  # Creamos una link para descargar la imagen
  image = requests.post('https://sandbox.hybridge.education/v2/utils/s3-signed-url', headers=HEADERS, json=BODY)

  # Carpeta donde deseas guardar la imagen
  save_folder = 'images'

  # Asegúrate de que la carpeta exista
  os.makedirs(save_folder, exist_ok=True)

  # Nombre del archivo de imagen
  image_name = os.path.basename(objectKey+'.png')

  # Ruta completa para guardar la imagen
  save_path = os.path.join(save_folder, image_name)

  # Descargar la imagen
  response = requests.get(image.json()['url'])

  # Verificar que la descarga fue exitosa
  if response.status_code == 200:
      # Guardar la imagen en el sistema de archivos
      with open(save_path, 'wb') as file:
          file.write(response.content)
      print(f'Imagen guardada en {save_path}')
  else:
      print(f'Error al descargar la imagen: {response.status_code}')