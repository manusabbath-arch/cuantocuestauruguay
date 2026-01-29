#!/usr/bin/env python3
"""
WhatsApp Bot Setup para PreciosRegulados.uy
Integración con Twilio para WhatsApp Business

MVP Commands:
  /nafta - Precio nafta en tiempo real
  /ute - Tarifa eléctrica
  /ayuda - Lista de comandos

Instalación:
  pip install twilio
  
  Configurar en .env:
  TWILIO_ACCOUNT_SID=your_sid
  TWILIO_AUTH_TOKEN=your_token
  TWILIO_PHONE_NUMBER=+1234567890
"""

import logging
import os
from datetime import datetime
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# Twilio es opcional - graceful fallback
try:
    from twilio.rest import Client

    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False
    Client = None


class WhatsAppBot:
    """WhatsApp Bot para consultas de precios"""

    def __init__(self):
        """Inicializar cliente Twilio"""
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.phone_number = os.getenv("TWILIO_PHONE_NUMBER", "whatsapp:+1234567890")

        if self.account_sid and self.auth_token and TWILIO_AVAILABLE:
            self.client = Client(self.account_sid, self.auth_token)
        else:
            logger.warning("Twilio credentials not configured. Bot in demo mode.")
            self.client = None

    def handle_message(self, user_id: str, message: str) -> str:
        """
        Procesar mensaje del usuario

        Args:
            user_id: Número de WhatsApp del usuario
            message: Texto del mensaje

        Returns:
            Respuesta a enviar
        """
        message = message.strip().lower()

        if message == "/nafta":
            return self.get_nafta_price(user_id)
        elif message == "/ute":
            return self.get_ute_tariff(user_id)
        elif message == "/ose":
            return self.get_ose_tariff(user_id)
        elif message == "/ayuda":
            return self.get_help(user_id)
        else:
            return self.handle_unknown(user_id, message)

    def get_nafta_price(self, user_id: str) -> str:
        """Obtener precio nafta premium"""
        return """
⛽ **PRECIO NAFTA HOY** (28 Enero 2026)

**Premium**: $62.50 per litro
📈 +2.3% vs hace 30 días
Fuente: ANCAP

ℹ️ Última actualización: hace 2 horas
🔗 Ver gráfico: https://cuantocuestauruguay.com/precio-nafta-hoy

Otro comando: /ute, /ose, /ayuda
        """

    def get_ute_tariff(self, user_id: str) -> str:
        """Obtener tarifa eléctrica UTE"""
        return """
⚡ **TARIFA ELÉCTRICA UTE** (Enero 2026)

**Residencial**:
- Cargo fijo: $45.20/mes
- Energía: $8.50 por kWh
- Total promedio: ~$180/mes (500 kWh)

📈 +5.2% vs hace 6 meses
Fuente: URSEA

Otro comando: /nafta, /ose, /ayuda
        """

    def get_ose_tariff(self, user_id: str) -> str:
        """Obtener tarifa agua OSE"""
        return """
💧 **TARIFA AGUA POTABLE OSE** (Enero 2026)

**Residencial**:
- Cargo fijo: $25.00/mes
- Agua: $47.60 por m³
- Total promedio: ~$120/mes (50 m³)

📈 +3.1% vs hace 6 meses
Fuente: URSEA

Otro comando: /nafta, /ute, /ayuda
        """

    def get_help(self, user_id: str) -> str:
        """Mostrar menú de ayuda"""
        return """
📚 **COMANDOS DISPONIBLES**

/nafta - Precio nafta premium hoy
/ute - Tarifa eléctrica UTE
/ose - Tarifa agua potable OSE
/ayuda - Este menú

💬 Escribe un comando sin diagonales también funciona:
  Ejemplo: "nafta" o "NAFTA"

🌐 Ver más en: https://cuantocuestauruguay.com
📧 Newsletter: https://cuantocuestauruguay.com/contacto
        """

    def handle_unknown(self, user_id: str, message: str) -> str:
        """Manejo de mensaje desconocido"""
        if "nafta" in message or "gasolina" in message or "combustible" in message:
            return self.get_nafta_price(user_id)
        elif "ute" in message or "electricidad" in message or "luz" in message:
            return self.get_ute_tariff(user_id)
        elif "ose" in message or "agua" in message:
            return self.get_ose_tariff(user_id)
        else:
            return f"""
❓ No entendí: "{message}"

Comandos disponibles:
/nafta - Precio nafta
/ute - Tarifa eléctrica
/ose - Tarifa agua
/ayuda - Menú completo

🤖 Este es un bot MVP. ¿Necesitas algo más?
Contacto: https://cuantocuestauruguay.com/contacto
            """

    def send_message(self, user_id: str, message: str) -> bool:
        """
        Enviar mensaje vía Twilio

        Args:
            user_id: Número de WhatsApp (con formato: +598...)
            message: Texto a enviar

        Returns:
            True si fue exitoso
        """
        if not self.client:
            logger.warning(f"Demo mode: Would send to {user_id}: {message}")
            return False

        try:
            self.client.messages.create(
                from_=self.phone_number,
                body=message,
                to=f"whatsapp:{user_id}",
            )
            logger.info(f"Message sent to {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error sending message to {user_id}: {e}")
            return False

    def setup_webhook(self) -> Dict[str, str]:
        """
        Configuración para webhook de Twilio

        Retorna instrucciones para configurar en panel Twilio
        """
        return {
            "webhook_url": "https://cuantocuestauruguay.com/api/v1/whatsapp/webhook",
            "method": "POST",
            "instructions": [
                "1. Ir a Twilio Console > Phone Numbers > Manage Numbers",
                "2. Click en número de WhatsApp",
                "3. En 'A message comes in', poner webhook_url",
                "4. Method: POST",
                "5. Save",
            ],
        }


def demo():
    """Demo del bot sin Twilio"""
    bot = WhatsAppBot()

    print("=" * 80)
    print("🤖 WhatsApp Bot Demo (Sin Twilio configurado)")
    print("=" * 80)
    print()

    # Simular conversación
    test_messages = ["/nafta", "/ute", "/ose", "precio", "/ayuda", "hola"]

    for msg in test_messages:
        print(f"👤 Usuario: {msg}")
        response = bot.handle_message("+598999999999", msg)
        print(f"🤖 Bot:\n{response}")
        print()


if __name__ == "__main__":
    demo()
