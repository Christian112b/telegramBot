import os

from telebot import *
from dotenv import load_dotenv

from functions.text import *
from functions.controller import *

load_dotenv()

telegram_token = os.getenv("telegram_token")
bot = telebot.TeleBot(token=telegram_token)

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
user_pedidos = {}

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

@bot.callback_query_handler(func=lambda call: call.data == "regalo")
def iniciar_recomendacion(call):
    regalo_contexto[call.message.chat.id] = {}
    markup = types.InlineKeyboardMarkup()
    opciones = [
        ("Pareja 💕", "pareja"),
        ("Mamá/Papá 👨‍👩‍👧", "familia"),
        ("Amigo/a 🎉", "amigo"),
        ("Cliente 🧑‍💼", "cliente"),
        ("Para mí 😋", "personal")
    ]
    for texto, valor in opciones:
        markup.add(types.InlineKeyboardButton(texto, callback_data=f"regalo_dest_{valor}"))
    bot.send_message(call.message.chat.id, "¿Para quién es el regalo?", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("regalo_dest_"))
def elegir_ocasion(call):
    chat_id = call.message.chat.id
    regalo_contexto[chat_id]["destinatario"] = call.data.split("_")[-1]
    markup = types.InlineKeyboardMarkup()
    opciones = [
        ("Cumpleaños 🎂", "cumple"),
        ("Aniversario 💍", "aniversario"),
        ("Agradecimiento 🙏", "agradecimiento"),
        ("Evento especial 🎊", "evento"),
        ("Solo porque sí 😋", "ocasional")
    ]
    for texto, valor in opciones:
        markup.add(types.InlineKeyboardButton(texto, callback_data=f"regalo_ocas_{valor}"))
    bot.send_message(chat_id, "¿Cuál es la ocasión?", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("regalo_ocas_"))
def elegir_estilo(call):
    chat_id = call.message.chat.id
    regalo_contexto[chat_id]["ocasion"] = call.data.split("_")[-1]
    markup = types.InlineKeyboardMarkup()
    opciones = [
        ("Elegante 🎩", "elegante"),
        ("Divertido 😄", "divertido"),
        ("Tradicional 🍬", "tradicional"),
        ("Sorpresivo 🎁", "sorpresivo")
    ]
    for texto, valor in opciones:
        markup.add(types.InlineKeyboardButton(texto, callback_data=f"regalo_estilo_{valor}"))
    bot.send_message(chat_id, "¿Qué estilo prefieres?", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("regalo_estilo_"))
def mostrar_recomendacion(call):
    chat_id = call.message.chat.id
    regalo_contexto[chat_id]["estilo"] = call.data.split("_")[-1]
    datos = regalo_contexto[chat_id]

    # Lógica condicional básica (puedes expandirla con más combinaciones)
    if datos["destinatario"] == "pareja" and datos["ocasion"] == "aniversario" and datos["estilo"] == "elegante":
        recomendacion = (
            "🎁 *Recomendación personalizada:*\n\n"
            "Te sugerimos la *Caja Duquesa*, con bombones rellenos de jalea de fresa y cobertura de chocolate amargo. "
            "Un detalle romántico y sofisticado para celebrar el amor. 💕"
        )
    elif datos["destinatario"] == "cliente":
        recomendacion = (
            "🎁 *Recomendación personalizada:*\n\n"
            "La *Caja Costanzo Corporativa* es ideal para clientes: elegante, neutra y con surtido variado. "
            "Perfecta para agradecimientos profesionales. 🧑‍💼"
        )
    else:
        recomendacion = (
            "🎁 *Recomendación personalizada:*\n\n"
            "Te sugerimos una *Caja Mixta*, con bombones, trufas y dulces tradicionales. "
            "Una opción versátil que se adapta a cualquier ocasión. 🍬"
        )

    bot.send_message(chat_id, recomendacion, parse_mode="Markdown")

    # Opcional: eliminar contexto
    regalo_contexto.pop(chat_id, None)

"""
    Modulo de testimonios. (Modulo propuesto por equipo de desarrollo)
    Aquí se maneja la interacción para mostrar testimonios de clientes satisfechos.
    Ruta: testimonios
"""
@bot.callback_query_handler(func=lambda call: call.data == "testimonios")
def mostrar_testimonios(call):
    mensajes = [
        "📣 *Ana, CDMX:* “Pedí una caja para mi aniversario y fue perfecta. ¡Gracias Costanzo!”",
        "📣 *Luis, SLP:* “Los chocolates rellenos de cajeta son una joya. Mi familia quedó encantada.”",
        "📣 *María, Querétaro:* “El empaque personalizado fue lo mejor. Ideal para regalar.”"
    ]
    for msg in mensajes:
        bot.send_message(call.message.chat.id, msg, parse_mode="Markdown")

bot.polling()