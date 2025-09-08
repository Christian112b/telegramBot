import os
from flask import Flask, request
from telebot import *
from dotenv import load_dotenv

from functions.text import *
from functions.controller import *

load_dotenv()

telegram_token = os.getenv("telegram_token")
bot = telebot.TeleBot(token=telegram_token)
app = Flask(__name__)

# Ruta para recibir actualizaciones desde Telegram
@app.route(f"/{telegram_token}", methods=["POST"])
def webhook():
    update = types.Update.de_json(request.get_data().decode("utf-8"))
    bot.process_new_updates([update])
    return "OK", 200

# Ruta de salud para Render
@app.route("/", methods=["GET"])
def index():
    return "Bot activo", 200

if __name__ == "__main__":
    bot.polling()



# # Configurar webhook al iniciar
# if __name__ == "__main__":
#     bot.remove_webhook()
#     bot.set_webhook(url=f"https://TU-APP-EN-RENDER.onrender.com/{telegram_token}")
#     app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))




"""
    Módulo para reiniciar el menú principal.
    Aquí se maneja la interacción para que el usuario pueda volver al menú principal en cualquier momento.
    Ruta: reiniciar
"""
@bot.callback_query_handler(func=lambda call: call.data == "reiniciar")
def volver_al_menu(call):
    reiniciar_menu(call)


"""
    Ruta para menú principal del bot.
    Espera a que el usuario envíe el comando /start para iniciar la interacción.
    Luego, muestra un menú con varias opciones utilizando botones inline.   
    
    Ruta: /start 
"""
@bot.message_handler(commands=['start'])
def welcome(message):
    msg_id = mostrar_menu_principal(message.chat.id)
    mensajes_activos[message.chat.id] = [msg_id]


"""
    Modulo de preguntas frecuentes.
    Aquí se manejan las interacciones relacionadas con las preguntas frecuentes de los usuarios.

    Ruta: preguntas_frecuentes
"""
@bot.callback_query_handler(func=lambda call: call.data == "preguntas_frecuentes")
def show_faq_menu(call):
    mostrar_faq_menu(call)


"""
    Modulo de respuestas a preguntas frecuentes.
    Aquí se manejan las respuestas a las preguntas frecuentes seleccionadas por el usuario.
    Ruta: faq_envios, faq_pago, faq_regalos, faq_horario
"""
@bot.callback_query_handler(func=lambda call: call.data in ["faq_envios", "faq_pago", "faq_regalos", "faq_horario"])
def answer_faq(call):
    desplegar_respuesta_faq(call)




"""
    Módulo para mostrar redes sociales.
    Esto maneja la interacción para que el usuario pueda contactar a través de redes sociales.
    Ruta: contacto
"""
@bot.callback_query_handler(func=lambda call: call.data == "contacto")
def contacto_humano(call):
    mostrar_contacto(call)


"""    
    Modulo de ubicación y sucursal más cercana. (Modulo propuesto por equipo de desarrollo)
    Aquí se maneja la interacción para obtener la ubicación del usuario y calcular la sucursal más cercana.
    Ruta: ubicacion
"""
@bot.callback_query_handler(func=lambda call: call.data == "ubicacion")
def request_location(call):
    pedir_ubicacion(call)


"""
    Módulo para recibir la ubicación del usuario y calcular la sucursal más cercana.
    Ruta: location
"""
@bot.message_handler(content_types=['location'])
def get_location(message):
    manejar_ubicacion(message)


"""
    Módulo para mostrar productos.
    Aquí se manejan la iteracion relacionadas con la visualización de productos.
    Ruta: productos
"""
@bot.callback_query_handler(func=lambda call: call.data == "productos")
def show_products(call):
    mostrar_productos(call)
    


"""
    Modulo para pedido personalizado.
    Generacion de flujo conversacional para recopilar detalles del pedido personalizado.
    Ruta: pedido_personalizado
"""
# Diccionario temporal para almacenar datos por usuario

# Iniciar el flujo de pedido personalizado
@bot.callback_query_handler(func=lambda call: call.data == "pedido_personalizado")
def start_order(call):
    iniciar_pedido_personalizado(call)

@bot.callback_query_handler(func=lambda call: call.data.startswith("ocasion_"))
def receive_occasion(call):
    recibir_ocasion(call)

@bot.callback_query_handler(func=lambda call: call.data.startswith("producto_"))
def receive_products(call):
    recibir_productos(call)

@bot.callback_query_handler(func=lambda call: call.data.startswith("cantidad_"))
def receive_quantity(call):
    recibir_cantidad(call)

@bot.callback_query_handler(func=lambda call: call.data.startswith("fecha_"))
def receive_date(call):
    recibir_fecha(call)

@bot.callback_query_handler(func=lambda call: call.data == "fecha")
def seleccionar_mes(call):
    chat_id = call.message.chat.id

    meses = [
        ("Septiembre", "mes_9"),
        ("Octubre", "mes_10"),
        ("Noviembre", "mes_11"),
        ("Diciembre", "mes_12")
    ]

    markup = types.InlineKeyboardMarkup()
    for nombre, callback in meses:
        markup.add(types.InlineKeyboardButton(nombre, callback_data=callback))

    msg = bot.send_message(chat_id, "Selecciona el mes para tu pedido:", reply_markup=markup)
    mensajes_activos.setdefault(chat_id, []).append(msg.message_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("mes_"))
def seleccionar_dia(call):
    chat_id = call.message.chat.id
    mes_num = int(call.data.split("_")[1])

    # Elimina el mensaje del selector de mes
    try:
        bot.delete_message(chat_id, call.message.message_id)
    except:
        pass  # Por si ya fue eliminado o no se puede borrar

     # Días del 1 al 30 para simplificar
    markup = types.InlineKeyboardMarkup()
    for dia in range(1, 31):
        fecha_str = f"{dia:02d}/{mes_num:02d}/2025"
        markup.add(types.InlineKeyboardButton(fecha_str, callback_data=f"fecha_{fecha_str}"))

    msg = bot.send_message(chat_id, "Selecciona el día disponible:", reply_markup=markup)
    mensajes_activos.setdefault(chat_id, []).append(msg.message_id)


@bot.message_handler(func=lambda message: message.chat.id in user_pedidos and "nombre" not in user_pedidos[message.chat.id])
def receive_nombre(call):
    recibir_nombre(call)

"""
    Módulo para salir del chat.
    Aquí se maneja la interacción para que el usuario pueda salir del chat de manera amigable
    Ruta: salir
"""
@bot.callback_query_handler(func=lambda call: call.data == "salir")
def salir_del_chat(call):
    bot.send_message(
        call.message.chat.id,
        "Gracias por visitar *Chocolates Costanzo* 🍫\n¡Esperamos verte pronto!"
    )

"""
    Módulo para recomendación de regalos. (Modulo propuesto por equipo de desarrollo)
    Aquí se maneja la interacción para recomendar regalos personalizados basados en las preferencias del usuario.
    Ruta: regalo
"""
# Diccionario temporal para almacenar respuestas por usuario
regalo_contexto = {}



# TODO: SEPARAR FUNCION PARA DEJAR ESTE ARCHIVO CON SOLAMENTE RUTA
regalo_contexto = {}

@bot.callback_query_handler(func=lambda call: call.data == "regalo")
def iniciar_recomendacion(call):
    chat_id = call.message.chat.id
    regalo_contexto[chat_id] = {}
    markup = types.InlineKeyboardMarkup()
    opciones = [
        ("Pareja", "pareja"),
        ("Mamá/Papá", "familia"),
        ("Amigo/a", "amigo"),
        ("Cliente", "cliente"),
        ("Para mí", "personal")
    ]
    for texto, valor in opciones:
        markup.add(types.InlineKeyboardButton(texto, callback_data=f"regalo_dest_{valor}"))

    msg = bot.send_message(chat_id, "¿Para quién es el regalo?", reply_markup=markup)
    mensajes_activos.setdefault(chat_id, []).append(msg.message_id)


@bot.callback_query_handler(func=lambda call: call.data.startswith("regalo_dest_"))
def elegir_ocasion(call):
    chat_id = call.message.chat.id
    regalo_contexto[chat_id]["destinatario"] = call.data.split("_")[-1]

    markup = types.InlineKeyboardMarkup()
    opciones = [
        ("Cumpleaños", "cumple"),
        ("Aniversario", "aniversario"),
        ("Agradecimiento", "agradecimiento"),
        ("Evento especial", "evento"),
        ("Solo porque sí", "ocasional")
    ]
    for texto, valor in opciones:
        markup.add(types.InlineKeyboardButton(texto, callback_data=f"regalo_ocas_{valor}"))

    msg = bot.send_message(chat_id, "¿Cuál es la ocasión?", reply_markup=markup)
    mensajes_activos.setdefault(chat_id, []).append(msg.message_id)


@bot.callback_query_handler(func=lambda call: call.data.startswith("regalo_ocas_"))
def elegir_estilo(call):
    chat_id = call.message.chat.id
    regalo_contexto[chat_id]["ocasion"] = call.data.split("_")[-1]

    markup = types.InlineKeyboardMarkup()
    opciones = [
        ("Elegante", "elegante"),
        ("Divertido", "divertido"),
        ("Tradicional", "tradicional"),
        ("Sorpresivo", "sorpresivo")
    ]
    for texto, valor in opciones:
        markup.add(types.InlineKeyboardButton(texto, callback_data=f"regalo_estilo_{valor}"))

    msg = bot.send_message(chat_id, "¿Qué estilo prefieres?", reply_markup=markup)
    mensajes_activos.setdefault(chat_id, []).append(msg.message_id)


@bot.callback_query_handler(func=lambda call: call.data.startswith("regalo_estilo_"))
def mostrar_recomendacion(call):
    chat_id = call.message.chat.id
    regalo_contexto[chat_id]["estilo"] = call.data.split("_")[-1]
    datos = regalo_contexto[chat_id]

    if datos["destinatario"] == "pareja" and datos["ocasion"] == "aniversario" and datos["estilo"] == "elegante":
        recomendacion = (
            "*Recomendación personalizada:*\n\n"
            "Te sugerimos la *Caja Duquesa*, con bombones rellenos de jalea de fresa y cobertura de chocolate amargo. "
            "Un detalle romántico y sofisticado para celebrar el amor."
        )
    elif datos["destinatario"] == "cliente":
        recomendacion = (
            "*Recomendación personalizada:*\n\n"
            "La *Caja Costanzo Corporativa* es ideal para clientes: elegante, neutra y con surtido variado. "
            "Perfecta para agradecimientos profesionales."
        )
    else:
        recomendacion = (
            "*Recomendación personalizada:*\n\n"
            "Te sugerimos una *Caja Mixta*, con bombones, trufas y dulces tradicionales. "
            "Una opción versátil que se adapta a cualquier ocasión."
        )

    msg1 = bot.send_message(chat_id, recomendacion, parse_mode="Markdown")
    mensajes_activos.setdefault(chat_id, []).append(msg1.message_id)

    # Botón para volver al menú
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Volver al menú principal", callback_data="reiniciar"))
    msg2 = bot.send_message(chat_id, "¿Deseas regresar al menú?", reply_markup=markup)
    mensajes_activos[chat_id].append(msg2.message_id)

    regalo_contexto.pop(chat_id, None)

"""
    Modulo de testimonios. (Modulo propuesto por equipo de desarrollo)
    Aquí se maneja la interacción para mostrar testimonios de clientes satisfechos.
    Ruta: testimonios
"""
@bot.callback_query_handler(func=lambda call: call.data == "testimonios")
def show_clients(call):
    mostrar_testimonios(call)

