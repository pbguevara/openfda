import http.server
import http.client
import socketserver
import json
#Para no cambiar el puerto
socketserver.TCPServer.allow_reuse_address = True

IP = "localhost"
PORT = 8000
headers = {'User-Agent': 'http-client'}

class testHTTPRequestHandler(http.server.BaseHTTPRequestHandler):

    def connect_open_fda(self, search = None, limit = 1):
        """Conecta el servidor con la FDA y realiza la peticion"""

        #Para conectar servidor y FDA
        conn = http.client.HTTPSConnection("api.fda.gov")

        #Peticion del usuario cuando solo introduce una cantidad (lista)
        request = '/drug/label.json/'+'?limit={}'.format(limit)

        #Peticion del usuario cuando introduce un principio activo o fabricante
        if search != None:
            request += '&search={}'.format(search)

        #traza: imprime la peticion en el server
        print('Petición: ', request)

        #Enviar peticion
        conn.request('GET', request, None, headers)

        #Obtener respuesta
        response = conn.getresponse()

        #EXTENSION II: Si no se ha hallado el recurso
        if response.status == 404:
            #traza: imprimir status en el servidor
            print('Error, no se ha podido encontrar el recurso.')
            self.display_error()


        #traza: Si se ha hallado el recurso (200 OK)
        print(response.status, response.reason)

        #Leer contenido del JSON y cerrar la conexion
        data_json = response.read().decode("utf-8")
        conn.close()
        #print(data_json)

        #Para convertir el JSON en datos de Python
        data = json.loads(data_json)

        return data

#-------------------------------------------------------------------------------

    def display_error(self):
        with open('error.html','r') as f:
            content = f.read()
            self.send_error(404, 'File Not Found')
            #self.wfile.write(bytes(content, "utf8"))
            return content

#-------------------------------------------------------------------------------

    def display_error_limit(self):
        with open('error_limit.html','r') as f:
            content = f.read()
            self.send_response(404)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(bytes(content, "utf8"))
            return content

#-------------------------------------------------------------------------------

    def find_drug(self, search = None, limit = 10):
        """Devuelve el medicamento o la lista de medicamentos solicitado(s)"""

        #Conectar el servidor con la FDA
        drug = self.connect_open_fda(search, limit)

        #Inicio del fichero HTML respuesta
        message = ('<!DOCTYPE html>\n'
                   '<html lang="en">\n'
                   '<head>\n'
                        '<meta charset="UTF-8">\n'
                        '<title>Medicamentos FDA</title>\n'
                   '</head>\n'
                   '<body>\n'
                   '<ul>\n'
                   )

        #META (informacion de búsqueda de la FDA)
        meta = drug['meta']
        total = meta['results']['total'] #Objetos existentes
        limit = meta['results']['limit'] #Objetos recibidos
        message += '<h1>Resultados </h1>'
        message += '<h2>Se han recibido {} medicamentos de {}. </h2>'.format(limit, total)
        message += ('<br/>')

        #RESULTS (resultados de la búsqueda)
        #La variable drugs contiene todos los objetos recibidos
        drugs = drug['results']
        for drug in drugs:
        #Para obtener los datos encontrados en 'openfda'
            if drug['openfda']:
                name = drug['openfda']['substance_name'][0]
                brand = drug['openfda']['brand_name'][0]
                manufacturer = drug['openfda']['manufacturer_name'][0]
        #Opcion por si no se encuentran esos datos
            else:
                name = 'Desconocido'
                brand = 'Desconocido'
                manufacturer = 'Desconocido'

        #Para obtener el ID del medicamento
            drug_id = drug['id']

        #Para obtener el proposito del medicamento
            try:
                purpose = drug['purpose'][0]
            except KeyError:
                purpose = 'Desconocido'

        #Añadir la informacion a la respuesta HTML
            message += "<li>Nombre: {}. Marca: {}. Fabricante: {}. ID: {}. Proposito: {}.</li>\n".format(name, brand, manufacturer, drug_id, purpose)
        message += '<br/>'
        message += '<a href="http://localhost:8000/">Volver al Inicio</a>'

        #Acabar la respuesta HTML
        message +=('</ul>\n'
                   '</body>\n'
                   '</html>')

        return message

#-------------------------------------------------------------------------------

    def find_company(self, search = None, limit = 10):
        """Devuelve la empresa o la lista de empresas solicitada(s)"""

        #Conectar el servidor con la FDA
        company = self.connect_open_fda(search, limit)

        #Inicio del fichero HTML respuesta
        message = ('<!DOCTYPE html>\n'
                   '<html lang="en">\n'
                   '<head>\n'
                        '<meta charset="UTF-8">\n'
                        '<title>Empresas FDA</title>\n'
                   '</head>\n'
                   '<body>\n'
                   '<ul>\n'
                   )

        #META
        meta = company['meta']
        total = meta['results']['total'] #Objetos existentes
        limit = meta['results']['limit'] #Objetos recibidos

        message += '<h1>Resultados </h1>'
        message += '<h2>Se han recibido {} empresas de {}. </h2>'.format(limit, total)
        message += ('<br/>')


        #RESULTS
        empresas = company['results']
        for company in empresas:
            if company['openfda']:
                if company['openfda']['manufacturer_name']:
                    company_name = company['openfda']['manufacturer_name'][0]
                else:
                    company_name = 'Desconocido'
            else:
                company = 'Desconocido'

            #Añadir la informacion a la respuesta HTML
            message += '<li>Empresa: {}</li>'.format(company_name)
        message += '<br/>'
        message += '<a href="http://localhost:8000/">Volver al Inicio</a>'

        #Acabar la respuesta HTLML
        message +=('</ul>\n'
                   '</body>\n'
                   '</html>')

        return message

#-------------------------------------------------------------------------------

    def find_warnings(self, search = None, limit = 10):
        """Devuelve una lista de advertencias"""

        #Conectar el servidor con la FDA
        warning = self.connect_open_fda(search, limit)

        #Inicio del fichero HTML respuesta
        message = ('<!DOCTYPE html>\n'
                   '<html lang="en">\n'
                   '<head>\n'
                        '<meta charset="UTF-8">\n'
                        '<title>Empresas FDA</title>\n'
                   '</head>\n'
                   '<body>\n'
                   '<ul>\n'
                   )

        #META
        meta = warning['meta']
        total = meta['results']['total'] #Objetos existentes
        limit = meta['results']['limit'] #Objetos recibidos

        message += '<h1>Resultados </h1>'
        message += '<h2>Se han recibido {} advertencias de {}. </h2>'.format(limit, total)
        message += ('<br/>')


        #RESULTS
        advertencias = warning['results']
        for warning in advertencias:
            try:
                drug_warning = warning['warnings'][0]
            except KeyError:
                drug_warning = 'Desconocido'


            #Añadir la informacion a la respuesta HTML
            message += '<li>Advertencia: {}</li>'.format(drug_warning)
        message += '<br/>'
        message += '<a href="http://localhost:8000/">Volver al Inicio</a>'

        #Acabar la respuesta HTLML
        message +=('</ul>\n'
                   '</body>\n'
                   '</html>')

        return message

#-------------------------------------------------------------------------------

    def do_GET(self):
        """Atiende peticiones GET por HTTP.
        El recurso solicitado se encuentra en la URL (path)."""

        global drug
        #traza: imprime la URL
        print('Path: ', self.path)

        #Convertir la URL en una lista para obtener los parametros
        recurso = self.path.split('?')
        path_request = recurso[0]
        print(path_request)

        #Solo mide 1 cuando no tiene parametros (formulario)
        if len(recurso) == 1:
            path_parameters = ''
        #Mide más de 1 cuando ya tiene parámetros.
        else:
            path_parameters = recurso[1]

        if path_parameters:
            #Crear una lista con el nombre del parametro y su valor
            data = path_parameters.split('=')

            if data[0]=='active_ingredient':
                drug = data[1]
            elif data[0] == 'company':
                company = data[1]
            elif data[0] == "limit":
                try:
                    limit = int(data[1])
                    if limit < 0:
                        self.display_error_limit()

                except:
                    self.display_error_limit()



        #Empezamos con los HTML
        try:
            #FORMULARIO_FDA
            if path_request == '/':
                with open('formulario_FDA.html', 'r')as f:
                    content = f.read()
                    message = content

            #MEDICAMENTOS
            elif path_request.startswith('/searchDrug'):
                message = self.find_drug(search = 'active_ingredient:'+drug)

            #LISTA DE MEDICAMENTOS
            elif path_request == '/listDrugs':
                message = self.find_drug(limit = limit)

            #EMPRESAS
            elif path_request.startswith('/searchCompany'):
                message = self.find_company(search = 'openfda.manufacturer_name:'+company)

            #LISTA DE EMPRESAS
            elif path_request == '/listCompanies':
                message = self.find_company(limit = limit)

            #LISTA DE ADVERTENCIAS ------------- EXT I
            elif path_request == '/listWarnings':
                message = self.find_warnings(limit = limit)

            #RECURSO NO ENCONTRADO ------------- EXT II
            elif path_request == '/not_exists_resource':
                self.send_error(404, 'File Not Found')
                message = ''
                condition = False

            #REDIRECT -------------------------- EXT IV
            elif path_request == '/redirect':
                self.send_response(302)
                self.send_header('Location', 'http://localhost:8000')
                self.end_headers()
                message = ''
                condition = False

            #SECRET ---------------------------- EXT IV
            elif path_request == '/secret':
                self.send_response(401)
                self.send_header('WWW-Authenticate', 'Basic realm=\""')
                self.end_headers()
                message = ''
                condition = False

            condition = True
            while condition:

                #Enviar la respuesta cuando todo sale bien
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                #Enviar el mensaje
                self.wfile.write(bytes(message, "utf8"))
                return


        except OSError:
            print('File Not Found')
            self.send_error(404, 'File Not Found')



#-------------------------------------------------------------------------------

# Inicio del servidor
# Handler = Nuestra Clase
Handler = testHTTPRequestHandler

# Configurar el socket del servidor
with socketserver.TCPServer((IP, PORT), Handler) as httpd:
    print("El servidor se encuentra en el puerto", PORT)

    # Bucle principal
    # Cada vez que se ocurra un "GET" se invoca al metodo do_GET del Handler
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("")
        print("Ejecucion del servidor interrumpida por el usuario.")

print("")
print("El servidor se ha detenido.")
