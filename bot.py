import os

from telebot import *
from dotenv import load_dotenv

from functions.text import *
from functions.controller import *

load_dotenv()

telegram_token = os.getenv("telegram_token")
bot = telebot.TeleBot(token=telegram_token)

# Mensaje de bienvenida y menú principal
@bot.message_handler(commands=['start'])
def welcome(message):
    mostrar_menu_principal(message.chat.id)

def mostrar_menu_principal(chat_id):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Preguntas frecuentes", callback_data="preguntas_frecuentes"))
    markup.add(types.InlineKeyboardButton("Productos", callback_data="productos"))
    markup.add(types.InlineKeyboardButton("Contactanos a nuestras redes sociales.", callback_data="contacto"))
    markup.add(types.InlineKeyboardButton("Solicitar pedido personalizado", callback_data="pedido_personalizado"))
    markup.add(types.InlineKeyboardButton("Salir", callback_data="salir"))

    bot.send_message(chat_id, welcome_message, reply_markup=markup)



# Menu de preguntas frecuentes
@bot.callback_query_handler(func=lambda call: call.data == "preguntas_frecuentes")
def show_faq_menu(call):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Conocer la sucursal más cercana", callback_data="faq_ubicacion"))
    markup.add(types.InlineKeyboardButton("¿Se realizan envíos a domicilio?", callback_data="faq_envios"))
    markup.add(types.InlineKeyboardButton("¿Cuáles son las formas de pago?", callback_data="faq_pago"))
    markup.add(types.InlineKeyboardButton("¿Se pueden hacer regalos personalizados?", callback_data="faq_regalos"))
    markup.add(types.InlineKeyboardButton("¿Cuál es el horario de atención?", callback_data="faq_horario"))

    bot.send_message(call.message.chat.id, "Selecciona una opción:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "faq_ubicacion")
def pedir_ubicacion(call):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    location_btn = types.KeyboardButton("📍 Enviar mi ubicación", request_location=True)
    markup.add(location_btn)

    bot.send_message(
        call.message.chat.id,
        "Por favor, comparte tu ubicación para ayudarte mejor:",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data in ["faq_envios", "faq_pago", "faq_regalos", "faq_horario"])
def answer_faq(call):
    respuesta = faq_respuestas.get(call.data, "Lo siento, no encontré esa pregunta.")
    bot.send_message(call.message.chat.id, respuesta, parse_mode="Markdown")

    bot.send_message(
        call.message.chat.id,
        "¿Deseas ver otra pregunta frecuente?",
        reply_markup=types.InlineKeyboardMarkup().add(
            types.InlineKeyboardButton("Volver a preguntas frecuentes", callback_data="preguntas_frecuentes")
        )
    )

@bot.message_handler(content_types=['location'])
def recibir_ubicacion(message):
    lat = message.location.latitude
    lon = message.location.longitude

    remove_markup = types.ReplyKeyboardRemove()
    sucursal, distancia = sucursal_mas_cercana(lat, lon)

    bot.send_message(
        message.chat.id,
        f"📍 La sucursal más cercana es *{sucursal['nombre']}*, a aproximadamente *{distancia} km* de tu ubicación.",
        parse_mode="Markdown",
        reply_markup=remove_markup
    )

    bot.send_message(
        message.chat.id,
        "¿Deseas ver otra pregunta frecuente?",
        reply_markup=types.InlineKeyboardMarkup().add(
            types.InlineKeyboardButton("Volver a preguntas frecuentes", callback_data="preguntas_frecuentes")
        )
    )


    bot.send_location(message.chat.id, sucursal["lat"], sucursal["lon"])

import time

@bot.callback_query_handler(func=lambda call: call.data == "productos")
def mostrar_productos(call):

    # Mensaje inicial
    bot.send_message(
        call.message.chat.id,
        "Te muestro los chocolates más populares de nuestra marca:"
    )

    # Mostrar productos con pausa entre cada uno
    for producto in productos:
        bot.send_photo(
            call.message.chat.id,
            photo=open(producto['imagen'], 'rb'),
            caption=f"*{producto['nombre']}*\n{producto['descripcion']}",
            parse_mode="Markdown"
        )
        time.sleep(1.5)  # Pausa de 1.5 segundos entre productos

    # Mensaje final y retorno a menú principal
    bot.send_message(call.message.chat.id, "Gracias por explorar nuestros productos. Aquí tienes el menú principal nuevamente:")
    mostrar_menu_principal(call.message.chat.id)

# Modulo de contacto humano
@bot.callback_query_handler(func=lambda call: call.data == "contacto")
def contacto_humano(call):
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
    markup.add(types.InlineKeyboardButton("Volver al menú principal", callback_data="start"))

    bot.send_message(call.message.chat.id, mensaje, parse_mode="Markdown", reply_markup=markup)


# Diccionario temporal para almacenar datos por usuario
user_pedidos = {}

# Modulo de Flujo conversacional para pedido personalizado
@bot.callback_query_handler(func=lambda call: call.data == "pedido_personalizado")
def iniciar_pedido(call):
    bot.send_message(call.message.chat.id, "¿Para qué ocasión es tu pedido? (Ej. cumpleaños, aniversario, evento corporativo)")
    bot.register_next_step_handler(call.message, recibir_ocasion)

def recibir_ocasion(message):
    user_pedidos[message.chat.id] = {"ocasion": message.text}
    bot.send_message(message.chat.id, "¿Qué tipo de productos deseas incluir? (Ej. bombones, trufas, surtido mixto)")
    bot.register_next_step_handler(message, recibir_productos)

def recibir_productos(message):
    user_pedidos[message.chat.id]["productos"] = message.text
    bot.send_message(message.chat.id, "¿Cuántas unidades o cajas necesitas?")
    bot.register_next_step_handler(message, recibir_cantidad)

def recibir_cantidad(message):
    user_pedidos[message.chat.id]["cantidad"] = message.text
    bot.send_message(message.chat.id, "¿Para qué fecha necesitas el pedido?")
    bot.register_next_step_handler(message, recibir_fecha)

def recibir_fecha(message):
    user_pedidos[message.chat.id]["fecha"] = message.text
    bot.send_message(message.chat.id, "¿A qué nombre registramos el pedido?")
    bot.register_next_step_handler(message, recibir_nombre)

def recibir_nombre(message):
    user_pedidos[message.chat.id]["nombre"] = message.text
    resumen = user_pedidos[message.chat.id]
    bot.send_message(
        message.chat.id,
        f"Tu pedido ha sido registrado:\n\n"
        f"Ocasión: {resumen['ocasion']}\n"
        f"Productos: {resumen['productos']}\n"
        f"Cantidad: {resumen['cantidad']}\n"
        f"Fecha: {resumen['fecha']}\n"
        f"Nombre: {resumen['nombre']}\n\n"
        "Un asesor se pondrá en contacto contigo para confirmar los detalles."
    )
    # Opcional: volver al menú principal
    mostrar_menu_principal(message.chat.id)



bot.polling()