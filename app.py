from flask import Flask, request, Response, render_template_string, jsonify
import qrcode
from xhtml2pdf import pisa
import base64
import io

app = Flask(__name__)

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Generar Etiqueta</title>
    </head>
    <body>
        <h1>Generar Etiqueta</h1>
        <form method="POST" action="/generar_etiqueta">
            <label for="numero_orden">Número de Orden:</label>
            <input type="text" name="numero_orden" required><br><br>

            <label for="nombre_completo">Nombre Completo:</label>
            <input type="text" name="nombre_completo" required><br><br>

            <label for="telefono">Teléfono:</label>
            <input type="text" name="telefono" required><br><br>

            <label for="direccion">Dirección:</label>
            <input type="text" name="direccion" required><br><br>

            <label for="cantidad_paquetes">Cantidad de Paquetes:</label>
            <input type="text" name="cantidad_paquetes" required><br><br>

            <label for="direccion_origen">Dirección de Origen:</label>
            <input type="text" name="direccion_origen" required><br><br>

            <label for="observaciones">Observaciones:</label>
            <textarea name="observaciones" rows="4" cols="50" required></textarea><br><br>

            <input type="submit" value="Generar Etiqueta">
        </form>
    </body>
    </html>
    '''

@app.route('/generar_etiqueta', methods=['POST'])
def generar_etiqueta():
    try:
        if request.form:
            datos = request.form
        else:
            datos = request.json

        numero_orden = datos['numero_orden']
        nombre_completo = datos['nombre_completo']
        telefono = datos['telefono']
        direccion = datos['direccion']
        cantidad_paquetes = datos['cantidad_paquetes']
        direccion_origen = datos['direccion_origen']
        observaciones = datos['observaciones']

        nombre_cliente = "PATPRIMO"

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(numero_orden)
        qr.make(fit=True)

        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_img = qr_img.resize((100, 100))  # Resize the QR code to 100x100px

        buffer = io.BytesIO()
        qr_img.save(buffer, format="PNG")
        qr_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

        etiqueta_html = render_template_string('''
            <!DOCTYPE html>
            <html>
            <head>
                <title>Etiqueta</title>
                <style>
                    .etiqueta {
                        font-family: Arial, sans-serif;
                        text-align: center;
                        margin: 10px;
                        padding: 10px;
                        width: 10cm;
                        height: 10cm;
                        border: 2px solid black;
                        display: grid;
                        grid-template-rows: 1fr 1fr 1fr;
                        grid-template-columns: 1fr 1fr 1fr;
                        grid-template-areas:
                            "logo numero cantidad"
                            "origen origen origen"
                            "destino destino destino"
                            "qr qr qr";
                    }
                    .logo {
                        grid-area: logo;
                        padding: 10px;
                        text-align: left;
                    }
                    .logo img {
                        width: 100px;
                        height: 100px;
                    }
                    .numero {
                        grid-area: numero;
                        text-align: center;
                    }
                    .cantidad {
                        grid-area: cantidad;
                        text-align: right;
                    }
                    .origen {
                        grid-area: origen;
                        text-align: center;
                    }
                    .destino {
                        grid-area: destino;
                        text-align: center;
                    }
                    .qr {
                        grid-area: qr;
                        text-align: center;
                    }
                </style>
            </head>
            <body>
                <div class="etiqueta">
                    <div class="logo">
                        <img src="yango_logo.png" alt="Logo de Yango Deliver" />
                    </div>
                    <div class="numero">
                        <label>Número de Orden:</label><br>
                        {{ numero_orden }}
                    </div>
                    <div class="cantidad">
                        <label>Cantidad de Paquetes:</label><br>
                        {{ cantidad_paquetes }}
                    </div>
                    <div class="origen">
                        <label>Dirección de Origen:</label><br>
                        {{ direccion_origen }}
                    </div>
                    <div class="destino">
                        <label>Dirección de Destino:</label><br>
                        {{ direccion }}
                    </div>
                    <div class="qr">
                        <img src="data:image/png;base64,{{ qr_base64 }}" alt="Código QR" />
                    </div>
                </div>
            </body>
            </html>
        ''',
        numero_orden=numero_orden,
        cantidad_paquetes=cantidad_paquetes,
        direccion_origen=direccion_origen,
        direccion=direccion,
        qr_base64=qr_base64,
        )

        pdf_buffer = io.BytesIO()
        pisa.CreatePDF(etiqueta_html, dest=pdf_buffer)

        pdf_buffer.seek(0)
        response = Response(pdf_buffer.read(), content_type='application/pdf')
        response.headers['Content-Disposition'] = 'inline; filename=etiqueta.pdf'

        return response
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
