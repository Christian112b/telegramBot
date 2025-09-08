from telebot import *

from math import radians, cos, sin, sqrt, atan2

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





"""
    Función para mostrar el menú principal con opciones.
    Utiliza botones inline para que el usuario pueda seleccionar una opción.
"""
def mostrar_menu_principal(chat_id):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Preguntas frecuentes", callback_data="preguntas_frecuentes"))
    markup.add(types.InlineKeyboardButton("Productos", callback_data="productos"))
    markup.add(types.InlineKeyboardButton("Contactanos a nuestras redes sociales.", callback_data="contacto"))
    markup.add(types.InlineKeyboardButton("Solicitar pedido personalizado", callback_data="pedido_personalizado"))
    markup.add(types.InlineKeyboardButton("Conocer la sucursal más cercana", callback_data="ubicacion"))
    markup.add(types.InlineKeyboardButton("Salir", callback_data="salir"))

    bot.send_message(chat_id, welcome_message, reply_markup=markup)