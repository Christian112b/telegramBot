import os
import time

from telebot import *

from dotenv import load_dotenv
from math import radians, cos, sin, sqrt, atan2

from functions.text import *

load_dotenv()

telegram_token = os.getenv("telegram_token")
bot = telebot.TeleBot(token=telegram_token)

mensajes_activos = {} 
user_pedidos = {}




sucursales = [ 
    {"nombre": "Costanzo Plaza Sendero", "lat": 22.13275796603885, "lon": -100.9234925442855},
    {"nombre": "Costanzo B. Anaya", "lat": 22.14722733539777, "lon": -100.93791209982348},
    {"nombre": "Costanzo Eje vial", "lat": 22.15546180242309, "lon": -100.97445755677404},
    {"nombre": "Costanzo Walmart 57", "lat": 22.138384583756316, "lon": -100.93508870462921},
    {"nombre": "Costanzo Cineteca", "lat": 22.150782469187842, "lon": -100.97317657495084},
    {"nombre": "Costanzo Calzada", "lat": 22.1434090279354, "lon": -100.97356281304562},
    {"nombre": "Costanzo Carranza", "lat": 22.151690586469375, "lon": -100.97911525030467},
    {"nombre": "Costanzo Galeana", "lat": 22.148924959202485, "lon": -100.97771688099583},
    {"nombre": "Costanzo 5 de mayo", "lat": 22.151744826015072, "lon": -100.9767838345836},
    {"nombre": "Costanzo Zapata", "lat": 22.14722733539777, "lon": -100.9872122631423}, 
    {"nombre": "Costanzo Macro plaza", "lat": 22.14351681233665, "lon": -100.95661362296798},
    {"nombre": "Costanzo Obregon", "lat": 22.15293704683907, "lon": -100.97567784632668},
    {"nombre": "Costanzo Walmart San Remo", "lat": 22.110089840111353, "lon": -100.89258757876674},
    {"nombre": "Costanzo Himno Nacional", "lat": 22.134624455571394, "lon": -100.9803207350378},
    {"nombre": "Costanzo Plaza Tangamanga   ", "lat": 22.14022235763719, "lon": -100.99981130094214}, 
    {"nombre": "Costanzo Himalaya", "lat": 22.142473532222436, "lon": -101.03241501384034},  
    {"nombre": "Costanzo Soledad", "lat": 22.14488445574455, "lon": -101.02002379824873},
    {"nombre": "Costanzo The Park", "lat": 22.123086811830767, "lon": -101.004939666254} 
]

def calcular_distancia(lat1, lon1, lat2, lon2):
    R = 6371  # Radio de la Tierra en km
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

def sucursal_mas_cercana(lat_usuario, lon_usuario):
    menor_distancia = float('inf')
    sucursal_cercana = None

    for sucursal in sucursales:
        dist = calcular_distancia(lat_usuario, lon_usuario, sucursal["lat"], sucursal["lon"])
        if dist < menor_distancia:
            menor_distancia = dist
            sucursal_cercana = sucursal

    return sucursal_cercana, round(menor_distancia, 2)


def borrar_mensajes(chat_id):
    if chat_id in mensajes_activos:
        for msg_id in mensajes_activos[chat_id]:
            try:
                bot.delete_message(chat_id, msg_id)
            except:
                pass
        mensajes_activos[chat_id] = []


"""
    Función para mostrar el menú principal con opciones.
    Utiliza botones inline para que el usuario pueda seleccionar una opción.
"""
def mostrar_menu_principal(chat_id):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Ver Preguntas frecuentes", callback_data="preguntas_frecuentes"))
    markup.add(types.InlineKeyboardButton("Ver nuestros productos mas populares", callback_data="productos"))
    markup.add(types.InlineKeyboardButton("Contactanos a nuestras redes sociales.", callback_data="contacto"))
    markup.add(types.InlineKeyboardButton("Solicitar pedido personalizado", callback_data="pedido_personalizado"))
    markup.add(types.InlineKeyboardButton("Conocer la sucursal más cercana", callback_data="ubicacion"))
    markup.add(types.InlineKeyboardButton("Recomendaciones para regalos", callback_data="regalo"))
    markup.add(types.InlineKeyboardButton("Ver testimonio de cliente", callback_data="testimonios"))
    markup.add(types.InlineKeyboardButton("Salir", callback_data="salir"))
    
    sent = bot.send_message(chat_id, welcome_message, reply_markup=markup)

    # Guardamos ID para eliminar el mensaje después
    return sent.message_id  


""" 
    Funcion de preguntas frecuentes.
    Aquí se maneja la interacción para mostrar preguntas frecuentes y sus respuestas.
"""
@bot.callback_query_handler(func=lambda call: call.data == "preguntas_frecuentes")
def mostrar_faq_menu(call):
    chat_id = call.message.chat.id

    # Elimina mensajes anteriores si existen
    if chat_id in mensajes_activos:
        for msg_id in mensajes_activos[chat_id]:
            try:
                bot.delete_message(chat_id, msg_id)
            except:
                pass
        mensajes_activos[chat_id] = []

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("¿Se realizan envíos a domicilio?", callback_data="faq_envios"))
    markup.add(types.InlineKeyboardButton("¿Cuáles son las formas de pago?", callback_data="faq_pago"))
    markup.add(types.InlineKeyboardButton("¿Se pueden hacer regalos personalizados?", callback_data="faq_regalos"))
    markup.add(types.InlineKeyboardButton("¿Cuál es el horario de atención?", callback_data="faq_horario"))
    markup.add(types.InlineKeyboardButton("🔙 Volver al menú principal", callback_data="reiniciar"))

    msg = bot.send_message(chat_id, "*Selecciona un tema:*", reply_markup=markup, parse_mode="Markdown")
    mensajes_activos[chat_id] = [msg.message_id]


"""
    Módulo para mostrar redes sociales.
    Esto maneja la interacción para que el usuario pueda contactar a través de redes sociales.
"""
def mostrar_contacto(call):
    chat_id = call.message.chat.id
    borrar_mensajes(chat_id)

    mensaje = (
        "*¿Deseas hablar con alguien de nuestro equipo?*\n\n"
        "Selecciona el canal que prefieras para contactarnos:"
    )

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Telegram – Atención Costanzo", url="https://t.me/CostanzoNoOficial"))
    markup.add(types.InlineKeyboardButton("WhatsApp – +52 444 431 2446", url="https://wa.me/524444312446"))
    markup.add(types.InlineKeyboardButton("Facebook", url="https://www.facebook.com/share/19ks8t5XPR/"))
    markup.add(types.InlineKeyboardButton("Instagram", url="https://www.instagram.com/chocolates_constanzo?igsh=cHF6bXBvZXU1ejRu&utm_source=qr"))
    markup.add(types.InlineKeyboardButton("TikTok", url="https://www.tiktok.com/@constanzonooficial?_t=ZS-8zPAEMamiWO&_r=1"))
    markup.add(types.InlineKeyboardButton("YouTube", url="https://www.youtube.com/@NoOficialChocolatesCostanzo"))
    markup.add(types.InlineKeyboardButton("X", url="https://x.com/ConstanzoNofic?t=bChosvweDOQ1aLe416alVg&s=09"))
    markup.add(types.InlineKeyboardButton("Volver al menú principal", callback_data="reiniciar"))

    msg = bot.send_message(chat_id, mensaje, parse_mode="Markdown", reply_markup=markup)

    mensajes_activos[chat_id] = [msg.message_id]

@bot.callback_query_handler(func=lambda call: call.data.startswith("faq_"))
def desplegar_respuesta_faq(call):
    chat_id = call.message.chat.id

    # Elimina mensajes anteriores si existen
    if chat_id in mensajes_activos:
        for msg_id in mensajes_activos[chat_id]:
            try:
                bot.delete_message(chat_id, msg_id)
            except:
                pass
        mensajes_activos[chat_id] = []

    respuesta = faq_respuestas.get(call.data, "Lo siento, no encontré esa pregunta.")
    msg1 = bot.send_message(chat_id, respuesta, parse_mode="Markdown")
    msg2 = bot.send_message(
        chat_id,
        "¿Deseas ver otra pregunta frecuente?",
        reply_markup=types.InlineKeyboardMarkup().add(
            types.InlineKeyboardButton("🔙 Volver a preguntas frecuentes", callback_data="preguntas_frecuentes")
        )
    )

    # Guarda los nuevos mensajes
    mensajes_activos[chat_id] = [msg1.message_id, msg2.message_id]

def reiniciar_menu(call):
    chat_id = call.message.chat.id

    # Elimina mensajes anteriores si existen
    if chat_id in mensajes_activos:
        for msg_id in mensajes_activos[chat_id]:
            try:
                bot.delete_message(chat_id, msg_id)
            except:
                pass
        mensajes_activos[chat_id] = []

    msg_id = mostrar_menu_principal(chat_id)

def mostrar_productos(call):
    chat_id = call.message.chat.id

    # Elimina mensajes anteriores si existen
    if chat_id in mensajes_activos:
        for msg_id in mensajes_activos[chat_id]:
            try:
                bot.delete_message(chat_id, msg_id)
            except:
                pass
        mensajes_activos[chat_id] = []

    ids = []  # Lista para guardar los nuevos mensajes

    # Mensaje inicial
    msg_intro = bot.send_message(chat_id, "Te muestro los chocolates más populares de nuestra marca:")
    ids.append(msg_intro.message_id)

    # Mostrar productos con pausa entre cada uno
    for producto in productos:
        msg_producto = bot.send_photo(
            chat_id,
            photo=open(producto['imagen'], 'rb'),
            caption=f"*{producto['nombre']}*\n{producto['descripcion']}",
            parse_mode="Markdown"
        )
        ids.append(msg_producto.message_id)
        time.sleep(1)

    # Mensaje final
    msg_final = bot.send_message(
        chat_id, 
        "Gracias por explorar nuestros productos.",
        reply_markup=types.InlineKeyboardMarkup().add(
            types.InlineKeyboardButton("🔙 Volver al menú principal", callback_data="reiniciar")
        )
    )
    ids.append(msg_final.message_id)

    # Registrar todos los mensajes
    mensajes_activos[chat_id] = ids

def manejar_ubicacion(message):
    chat_id = message.chat.id
    lat = message.location.latitude
    lon = message.location.longitude

    remove_markup = types.ReplyKeyboardRemove()
    sucursal, distancia = sucursal_mas_cercana(lat, lon)

    # Elimina mensajes anteriores si existen
    borrar_mensajes(chat_id)

    ids = []

    # Mensaje con texto
    msg1 = bot.send_message(
        chat_id,
        f"📍 La sucursal más cercana es *{sucursal['nombre']}*, a aproximadamente *{distancia} km* de tu ubicación.",
        parse_mode="Markdown",
        reply_markup=remove_markup
    )
    ids.append(msg1.message_id)

    # Mensaje con botón para volver
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 Volver a menu", callback_data="reiniciar"))
    msg2 = bot.send_message(chat_id, "¿Deseas volver al menú principal?", reply_markup=markup)
    ids.append(msg2.message_id)

    # Mensaje con ubicación
    msg3 = bot.send_location(chat_id, sucursal["lat"], sucursal["lon"])
    ids.append(msg3.message_id)

    mensajes_activos[chat_id] = ids

def pedir_ubicacion(call):

    chat_id = call.message.chat.id
    borrar_mensajes(chat_id)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    location_btn = types.KeyboardButton("📍 Enviar mi ubicación", request_location=True)
    markup.add(location_btn)

    msg = bot.send_message(
        call.message.chat.id,
        "Por favor, comparte tu ubicación para ayudarte mejor:",
        reply_markup=markup
    )

    mensajes_activos[chat_id] = [msg.message_id]

def iniciar_pedido_personalizado(call):
    chat_id = call.message.chat.id
    borrar_mensajes(chat_id)

    # Crear botones inline con opciones de ocasión
    markup = types.InlineKeyboardMarkup()
    opciones = [
        ("Cumpleaños", "ocasion_cumple"),
        ("Aniversario", "ocasion_aniversario"),
        ("Evento corporativo", "ocasion_evento"),
        ("Regalo personal", "ocasion_regalo"),
        ("Otro", "ocasion_otro")
    ]
    for texto, callback in opciones:
        markup.add(types.InlineKeyboardButton(texto, callback_data=callback))

    msg = bot.send_message(chat_id, "¿Para qué ocasión es tu pedido?", reply_markup=markup)
    mensajes_activos.setdefault(chat_id, []).append(msg.message_id)

def recibir_ocasion(call):
    chat_id = call.message.chat.id
    ocasion = call.data.split("_")[1]
    
    user_pedidos[chat_id] = {"ocasion": ocasion}

    # Crear botones inline para tipo de producto
    markup = types.InlineKeyboardMarkup()
    opciones = [
        ("Bombones", "producto_bombones"),
        ("Trufas", "producto_trufas"),
        ("Surtido mixto", "producto_surtido"),
        ("Caja personalizada", "producto_personalizada"),
        ("Otro", "producto_otro")
    ]
    for texto, callback in opciones:
        markup.add(types.InlineKeyboardButton(texto, callback_data=callback))

    msg = bot.send_message(chat_id, "¿Qué tipo de productos deseas incluir?", reply_markup=markup)
    mensajes_activos.setdefault(chat_id, []).append(msg.message_id)

def recibir_productos(call):
    chat_id = call.message.chat.id
    producto_key = call.data.split("_")[1]

    if chat_id not in user_pedidos:
        user_pedidos[chat_id] = {}

    user_pedidos[chat_id]["producto"] = producto_key

    nombres_legibles = {
        "bombones": "Bombones rellenos",
        "trufas": "Trufas artesanales",
        "surtido": "Surtido mixto",
        "personalizada": "Caja personalizada",
        "otro": "Otro tipo de producto"
    }

    producto_legible = nombres_legibles.get(producto_key, producto_key.capitalize())

    mensaje = (
        f"Excelente elección: *{producto_legible}*.\n\n"
        "¿Cuántas unidades deseas incluir en tu pedido?"
    )

    markup = types.InlineKeyboardMarkup()
    cantidades = [("1 unidad", "cantidad_1"), ("3 unidades", "cantidad_3"), ("Caja completa", "cantidad_caja")]
    for texto, callback in cantidades:
        markup.add(types.InlineKeyboardButton(texto, callback_data=callback))

    msg = bot.send_message(chat_id, mensaje, parse_mode="Markdown", reply_markup=markup)
    mensajes_activos.setdefault(chat_id, []).append(msg.message_id)

def recibir_cantidad(call):
    chat_id = call.message.chat.id
    cantidad_key = call.data.split("_")[1]

    if chat_id not in user_pedidos:
        user_pedidos[chat_id] = {}

    user_pedidos[chat_id]["cantidad"] = cantidad_key

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Seleccionar fecha", callback_data="fecha"))

    msg = bot.send_message(chat_id, "¿Para qué fecha necesitas el pedido?", reply_markup=markup)
    mensajes_activos.setdefault(chat_id, []).append(msg.message_id)

def recibir_fecha(call):
    chat_id = call.message.chat.id
    fecha = call.data.split("_")[1]

    if chat_id not in user_pedidos:
        user_pedidos[chat_id] = {}

    user_pedidos[chat_id]["fecha"] = fecha

    # Elimina el mensaje del selector de día
    try:
        bot.delete_message(chat_id, call.message.message_id)
    except:
        pass

    msg = bot.send_message(chat_id, "¿A qué nombre registramos el pedido?")
    mensajes_activos.setdefault(chat_id, []).append(msg.message_id)

def recibir_nombre(message):
    chat_id = message.chat.id
    user_pedidos[chat_id]["nombre"] = message.text
    resumen = user_pedidos[chat_id]

    nombres_legibles = {
        "bombones": "Bombones rellenos",
        "trufas": "Trufas artesanales",
        "surtido": "Surtido mixto",
        "personalizada": "Caja personalizada",
        "otro": "Otro tipo de producto"
    }
    producto_legible = nombres_legibles.get(resumen["producto"], resumen["producto"].capitalize())

    mensaje_resumen = (
        "Tu pedido ha sido registrado correctamente:\n\n"
        f"Ocasión: {resumen['ocasion'].capitalize()}\n"
        f"Producto: {producto_legible}\n"
        f"Cantidad: {resumen['cantidad']}\n"
        f"Fecha: {resumen['fecha']}\n"
        f"Nombre: {resumen['nombre']}\n\n"
        "Nos pondremos en contacto contigo pronto para confirmar los detalles.\n"
        "Gracias por confiar en nosotros."
    )

    # Crear botón para volver al menú
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Volver al menú principal", callback_data="reiniciar"))

    msg = bot.send_message(chat_id, mensaje_resumen, reply_markup=markup)
    mensajes_activos.setdefault(chat_id, []).append(msg.message_id)

def mostrar_testimonios(call):
    chat_id = call.message.chat.id

    # Borrar el mensaje del botón
    try:
        bot.delete_message(chat_id, call.message.message_id)
    except:
        pass

    # Enviar cada testimonio y registrar sus IDs
    mensajes_activos.setdefault(chat_id, [])
    
    for msg in mensajes:
        enviado = bot.send_message(chat_id, msg, parse_mode="Markdown")
        mensajes_activos[chat_id].append(enviado.message_id)

    # Btn para volver al menú
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Volver al menú principal", callback_data="reiniciar"))
    boton = bot.send_message(chat_id, "¿Deseas volver al menú?", reply_markup=markup)
    mensajes_activos[chat_id].append(boton.message_id)


