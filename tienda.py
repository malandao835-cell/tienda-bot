import os
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests

TOKEN = "8989087447:AAE3Sstkfd2bjI_jO5YPtmeRM61vg1y7Jb0"
BASE_URL = f"https://api.telegram.org/bot{TOKEN}/"

PRODUCTOS = [
    ("Movistar plus 1 año - 50€", "movistar_1y"),
    ("Gemini Pro Links 18 Meses - 50€", "gemini_18m"),
    ("CURSO VIP+METODO", "curso_vip"),
    ("Bot CHK", "bot_chk"),
    ("Gemini AI Private Method [100% Working] - 80€", "gemini_method"),
    ("Method Capcut 1 Year - 20€", "method_capcut"),
    ("Spotify 3 Meses - 5€", "spotify_3m"),
    ("BLAZZER 1 año - 10€", "blazzer_1y"),
    ("NETFLIX Premium 1 Month - 15$", "netflix_1m"),
    ("Orange TV", "orange_tv"),
    ("Amazon Prime 1 año - 30€", "amazon_1y")
]

CONTACTO = "@pepejean1"
CONTACTO_URL = "https://t.me/pepejean1"

class PingHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot activo 24/7")

def run_web():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), PingHandler)
    server.serve_forever()

def tg(metodo, datos):
    try:
        r = requests.post(BASE_URL + metodo, json=datos, timeout=10)
        return r.json()
    except:
        return {}

def get_menu():
    texto = (
        "🛍 <b>Productos de la tienda</b>\n"
        "Seleccione un producto para ver los detalles y realizar la compra:"
    )
    teclado = {
        "inline_keyboard": [
            [{"text": nombre, "callback_data": f"item_{cid}"}]
            for nombre, cid in PRODUCTOS
        ]
    }
    return texto, teclado

def bot_loop():
    print("--- TIENDA ONLINE ACTIVA ---")
    last = 0
    while True:
        try:
            r = tg("getUpdates", {"offset": last, "timeout": 5})
            for i in r.get("result", []):
                last = i["update_id"] + 1

                if "callback_query" in i:
                    q = i["callback_query"]
                    cid = q["message"]["chat"]["id"]
                    mid = q["message"]["message_id"]
                    data = q.get("data", "")
                    tg("answerCallbackQuery", {"callback_query_id": q["id"]})

                    if data.startswith("item_"):
                        item_id = data.replace("item_", "")
                        prod_nombre = next((n for n, c in PRODUCTOS if c == item_id), "Producto")
                        texto_adquirir = (
                            f"📦 <b>{prod_nombre}</b>\n\n"
                            f"ℹ️ Para adquirir este producto o consultar disponibilidad, contacta directamente con soporte:\n\n"
                            f"👤 <b>Atención:</b> {CONTACTO}"
                        )
                        kb_adquirir = {
                            "inline_keyboard": [
                                [{"text": "📩 Contactar soporte", "url": CONTACTO_URL}],
                                [{"text": "⬅️ Volver a la lista", "callback_data": "menu_principal"}]
                            ]
                        }
                        tg("editMessageText", {
                            "chat_id": cid,
                            "message_id": mid,
                            "text": texto_adquirir,
                            "parse_mode": "HTML",
                            "reply_markup": kb_adquirir
                        })

                    elif data == "menu_principal":
                        txt, kb = get_menu()
                        tg("editMessageText", {
                            "chat_id": cid,
                            "message_id": mid,
                            "text": txt,
                            "parse_mode": "HTML",
                            "reply_markup": kb
                        })

                elif "message" in i:
                    m = i["message"]
                    cid = m["chat"]["id"]
                    txt = m.get("text", "")
                    if txt:
                        txt_menu, kb_menu = get_menu()
                        tg("sendMessage", {
                            "chat_id": cid,
                            "text": txt_menu,
                            "parse_mode": "HTML",
                            "reply_markup": kb_menu
                        })
        except:
            pass
        time.sleep(1)

if __name__ == "__main__":
    threading.Thread(target=run_web, daemon=True).start()
    bot_loop()
