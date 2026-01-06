"""
Servicio de notificaciones por email para alertas de precios.
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict
import os
from dotenv import load_dotenv

load_dotenv()

# Configuración SMTP (desde variables de entorno)
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", SMTP_USER)


def send_price_alert_email(alert: Dict, company_name: str = "") -> Dict:
    """
    Envía email de alerta de precio.
    
    Args:
        alert: Dict con datos de la alerta (symbol, condition, target_price, current_price, email)
        company_name: Nombre de la empresa (opcional)
    
    Returns:
        Dict con status del envío
    """
    if not SMTP_USER or not SMTP_PASSWORD:
        return {
            "status": "error",
            "message": "Configuración SMTP no disponible. Configura SMTP_USER y SMTP_PASSWORD."
        }
    
    to_email = alert.get('email')
    if not to_email:
        return {"status": "error", "message": "Email no especificado en la alerta"}
    
    symbol = alert['symbol']
    condition = alert['condition']
    target_price = alert['target_price']
    current_price = alert['current_price']
    
    # Texto de la condición
    condition_text = "alcanzó o superó" if condition == "above" else "bajó de"
    
    # Nombre a mostrar
    display_name = f"{company_name} ({symbol})" if company_name else symbol
    
    # Crear mensaje
    msg = MIMEMultipart('alternative')
    msg['Subject'] = f"🔔 Alerta de Precio: {display_name}"
    msg['From'] = FROM_EMAIL
    msg['To'] = to_email
    
    # Contenido HTML
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; padding: 20px; background: #f5f5f5; }}
            .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; padding: 30px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
            .price {{ font-size: 32px; font-weight: bold; color: #667eea; margin: 20px 0; }}
            .info {{ background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 15px 0; }}
            .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔔 Alerta de Precio Activada</h1>
            </div>
            
            <h2>{display_name}</h2>
            
            <div class="info">
                <p><strong>Condición:</strong> El precio {condition_text} {target_price}€</p>
                <p><strong>Precio objetivo:</strong> {target_price}€</p>
                <p class="price">Precio actual: {current_price}€</p>
            </div>
            
            <p>Tu alerta de precio ha sido activada. Este es un mensaje automático del sistema IBEX 35 Trading API.</p>
            
            <div class="footer">
                <p>IBEX 35 Trading API - Sistema de Alertas</p>
                <p>Para gestionar tus alertas, accede a la plataforma web.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Texto plano alternativo
    text_content = f"""
    🔔 ALERTA DE PRECIO ACTIVADA
    
    {display_name}
    
    Condición: El precio {condition_text} {target_price}€
    Precio objetivo: {target_price}€
    Precio actual: {current_price}€
    
    Tu alerta de precio ha sido activada.
    
    ---
    IBEX 35 Trading API - Sistema de Alertas
    """
    
    # Adjuntar ambas versiones
    part1 = MIMEText(text_content, 'plain')
    part2 = MIMEText(html_content, 'html')
    msg.attach(part1)
    msg.attach(part2)
    
    try:
        # Conectar y enviar
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(FROM_EMAIL, to_email, msg.as_string())
        server.quit()
        
        return {
            "status": "sent",
            "to": to_email,
            "symbol": symbol,
            "message": "Email enviado correctamente"
        }
    
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error enviando email: {str(e)}"
        }


def test_email_config() -> Dict:
    """Prueba la configuración de email"""
    if not SMTP_USER or not SMTP_PASSWORD:
        return {
            "status": "error",
            "message": "Variables SMTP_USER y SMTP_PASSWORD no configuradas"
        }
    
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.quit()
        
        return {
            "status": "ok",
            "message": f"Conexión SMTP exitosa a {SMTP_SERVER}:{SMTP_PORT}",
            "smtp_user": SMTP_USER
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error de conexión SMTP: {str(e)}"
        }
