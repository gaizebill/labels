from flask import Flask, request, Response, render_template_string
import qrcode
from xhtml2pdf import pisa
import base64
import io

app = Flask(__name__)

@app.route('/generar_etiqueta', methods=['POST'])
def generar_etiqueta():
    try:
        datos = request.json
        numero_orden = datos['numero_orden']
        nombre_completo = datos['nombre_completo']
        telefono = datos['telefono']
        direccion = datos['direccion']

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
                    }
                    .nombre-cliente {
                        font-size: 16px;
                        margin: 5px 0;
                    }
                    .nombre-cliente-bold {
                        font-size: 16px;
                        font-weight: bold;
                        margin: 5px 0;
                    }
                    .codigo-qr {
                        margin-top: 10px;
                    }
                    .imagen-operador {
                        margin-top: 10px;
                    }
                    .logo {
                        margin-bottom: 10px;
                    }
                </style>
            </head>
            <body>
                <div class="etiqueta">
                    <div class="logo">
                        <img src="yango_logo.png" alt="Logo de Yango Deliver" width="300px" />
                    </div>
                    <div class="nombre-cliente-bold">{{ nombre_cliente }}</div>
                    <div class="nombre-cliente">{{ nombre_completo }}</div>
                    <div class="nombre-cliente">{{ telefono }}</div>
                    <div class="nombre-cliente">{{ direccion }}</div>
                    <div class="codigo-qr">
                        <img src="data:image/png;base64,{{ qr_base64 }}" alt="Código QR" />
                    </div>
                </div>
            </body>
            </html>
        ''',
        nombre_cliente=nombre_cliente,
        nombre_completo=nombre_completo,
        telefono=telefono,
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
