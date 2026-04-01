import os
import tempfile
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from openai import OpenAI

from task_validator import es_tarea_valida
from task_extractor import extraer_tarea
from task_storage import guardar_tarea
from calendar_utils import crear_evento_google

# Cargar variables (.env)
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Iniciar cliente de OpenAI
openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("¡Hola! Envíame una nota de voz con la tarea que quieres agendar y me encargaré del resto.")

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not openai_client:
        await update.message.reply_text("⚠️ No has configurado OPENAI_API_KEY en tu .env")
        return

    # Mensaje de progreso
    status_msg = await update.message.reply_text("⏳ Descargando audio desde Telegram...")

    # Obtener el archivo de voz
    voice_file = await context.bot.get_file(update.message.voice.file_id)
    
    # Guardar a un archivo temporal (.ogg)
    temp_dir = tempfile.gettempdir()
    audio_path = os.path.join(temp_dir, f"{update.message.voice.file_id}.ogg")
    await voice_file.download_to_drive(audio_path)

    # Transcribir con OpenAI API en la nube
    try:
        await status_msg.edit_text("⏳ Transcribiendo voz súper rápido con OpenAI...")
        with open(audio_path, "rb") as audio:
            transcription = openai_client.audio.transcriptions.create(
                model="whisper-1", 
                file=audio, 
                language="es"
            )
        texto_detectado = transcription.text
    except Exception as e:
        await status_msg.edit_text(f"❌ Error al transcribir: {str(e)}")
        if os.path.exists(audio_path): os.remove(audio_path)
        return

    # Limpiar archivo temporal
    if os.path.exists(audio_path):
        os.remove(audio_path)

    await status_msg.edit_text(f"🗣️ *Texto detectado:*\n_{texto_detectado}_", parse_mode="Markdown")

    # Validar y extraer tarea
    if es_tarea_valida(texto_detectado):
        tarea = extraer_tarea(texto_detectado)
        
        # Guardar contextualmente
        context.user_data['temp_tarea'] = tarea
        guardar_tarea(tarea)

        # Mostrar botones
        teclado = [
            [InlineKeyboardButton("📅 Agendar en Google Calendar", callback_data="cal_g")]
        ]
        reply_markup = InlineKeyboardMarkup(teclado)
        
        texto_tarea = f"✅ *¡Tarea Identificada!*\n• Acción: `{tarea.get('accion')}`\n• Título: `{tarea.get('titulo')}`\n• Día: `{tarea.get('fecha')}`\n• Hora: `{tarea.get('hora')}`\n\n¿Dónde quieres agendarlo?"
        await update.message.reply_text(texto_tarea, reply_markup=reply_markup, parse_mode="Markdown")
    else:
        await update.message.reply_text("⚠️ No pude reconocer una tarea (falta un verbo, fecha u hora). Inténtalo más claro.")


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    tarea = context.user_data.get('temp_tarea')
    if not tarea:
        await query.edit_message_text(text="⚠️ La tarea ya expiró o hubo un error al leer la memoria temporal.")
        return

    choice = query.data
    await query.edit_message_text(text="⏳ Conectando a Google Calendar...")

    # Agendar
    try:
        if choice == 'cal_g':
            crear_evento_google(tarea)
            msg = "✅ Evento agendado exitosamente en *Google Calendar*\n"
            await query.edit_message_text(text=f"¡Listo!\n{msg}", parse_mode="Markdown")
        
        # Opcional: limpiar la memoria tras éxito
        context.user_data['temp_tarea'] = None
    except Exception as e:
        await query.edit_message_text(text=f"❌ Ocurrió un error general: {e}")

if __name__ == '__main__':
    if not TELEGRAM_BOT_TOKEN or "pega_aqui" in TELEGRAM_BOT_TOKEN:
        print("❌ ALTO: Por favor, inserta tu Token de Telegram en el archivo oculto .env antes de iniciar")
        exit(1)
        
    print("🤖 Iniciando Servidor LIGERO del Bot de Telegram (Voice-to-Do)...")
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    app.add_handler(CallbackQueryHandler(button_callback))

    print("✅ Bot funcionando y escuchando mensajes nuevos... (Presiona Ctrl+C para apagarlo)")
    
    # Configuración de Render Webhook
    PORT = int(os.environ.get('PORT', 8443))
    RENDER_EXTERNAL_URL = os.environ.get('RENDER_EXTERNAL_URL')
    
    if RENDER_EXTERNAL_URL:
        print(f"🌍 Modo Cloud: Iniciando Webhooks en el puerto {PORT}")
        app.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            webhook_url=f"{RENDER_EXTERNAL_URL}/{TELEGRAM_BOT_TOKEN}"
        )
    else:
        print("💻 Modo Local: Iniciando Polling")
        app.run_polling()
