#!/usr/bin/env python3
"""
Newsletter Integration para CuantoCuestaUruguay.com
Usando Resend.com (SendGrid alternative, mejor para startups)

Setup:
  pip install resend
  
  .env:
  RESEND_API_KEY=re_...
"""

import json
import os
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

# Para demo, usamos un JSON file. En prod, usar Resend API
SUBSCRIBERS_FILE = "backend/data/newsletter_subscribers.json"


@dataclass
class Subscriber:
    """Modelo de suscriptor"""

    email: str
    name: Optional[str] = None
    subscribed_at: str = None
    tags: List[str] = None
    active: bool = True

    def __post_init__(self):
        if not self.subscribed_at:
            self.subscribed_at = datetime.now().isoformat()
        if not self.tags:
            self.tags = ["newsletter"]


class NewsletterManager:
    """Gestor de newsletter con Resend"""

    def __init__(self):
        """Inicializar gestor"""
        self.api_key = os.getenv("RESEND_API_KEY")
        self.from_email = "newsletter@cuantocuestauruguay.com"
        self.from_name = "PreciosRegulados.uy"

        # Para demo, usar archivo JSON
        self.use_api = bool(self.api_key)
        self._ensure_data_file()

    def _ensure_data_file(self):
        """Crear archivo de suscriptores si no existe"""
        import os
        from pathlib import Path

        data_dir = Path("backend/data")
        data_dir.mkdir(exist_ok=True)

        if not Path(SUBSCRIBERS_FILE).exists():
            with open(SUBSCRIBERS_FILE, "w") as f:
                json.dump({"subscribers": []}, f)

    def subscribe(self, email: str, name: str = None, tags: List[str] = None) -> bool:
        """
        Suscribir usuario a newsletter

        Args:
            email: Email del usuario
            name: Nombre (opcional)
            tags: Tags para segmentación (default: ["newsletter"])

        Returns:
            True si fue exitoso
        """
        subscriber = Subscriber(email=email, name=name, tags=tags or ["newsletter"])

        if self.use_api:
            return self._subscribe_via_api(subscriber)
        else:
            return self._subscribe_via_file(subscriber)

    def _subscribe_via_file(self, subscriber: Subscriber) -> bool:
        """Guardar suscriptor en archivo JSON (demo)"""
        try:
            with open(SUBSCRIBERS_FILE, "r") as f:
                data = json.load(f)

            # Verificar si ya existe
            if any(s["email"] == subscriber.email for s in data["subscribers"]):
                return False  # Ya existe

            data["subscribers"].append(
                {
                    "email": subscriber.email,
                    "name": subscriber.name,
                    "subscribed_at": subscriber.subscribed_at,
                    "tags": subscriber.tags,
                    "active": subscriber.active,
                }
            )

            with open(SUBSCRIBERS_FILE, "w") as f:
                json.dump(data, f, indent=2)

            return True
        except Exception as e:
            print(f"Error subscribing: {e}")
            return False

    def _subscribe_via_api(self, subscriber: Subscriber) -> bool:
        """Suscribir via Resend API"""
        try:
            import resend

            resend.api_key = self.api_key

            resend.Contacts.create(
                email=subscriber.email,
                list_id="cuantocuestauruguay",
                first_name=subscriber.name or "Usuario",
                tags=subscriber.tags,
            )
            return True
        except Exception as e:
            print(f"Error via Resend API: {e}")
            return False

    def send_weekly_digest(self, template: str = "default") -> dict:
        """
        Enviar digest semanal de precios

        Args:
            template: Nombre del template

        Returns:
            Estadísticas de envío
        """
        if self.use_api:
            return self._send_via_api_digest()
        else:
            return self._send_demo_digest()

    def _send_demo_digest(self) -> dict:
        """Demo de digest sin enviar realmente"""
        with open(SUBSCRIBERS_FILE, "r") as f:
            data = json.load(f)

        count = len(data["subscribers"])

        return {
            "status": "success",
            "message": f"Newsletter digest would be sent to {count} subscribers",
            "template": "weekly_digest",
            "count": count,
            "timestamp": datetime.now().isoformat(),
        }

    def _send_via_api_digest(self) -> dict:
        """Enviar via Resend API"""
        try:
            import resend

            resend.api_key = self.api_key

            # Template: resumen semanal de precios
            html = self._get_weekly_digest_html()

            email = resend.Emails.send(
                from_=f"{self.from_name} <{self.from_email}>",
                to="cuantocuestauruguay@resend.dev",  # Test
                subject="📊 Resumen Semanal de Precios (Sem. 4 Enero)",
                html=html,
            )

            return {
                "status": "success",
                "email_id": email["id"],
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
            }

    def _get_weekly_digest_html(self) -> str:
        """HTML del digest semanal"""
        return """
        <html>
            <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px; text-align: center; border-radius: 8px 8px 0 0;">
                    <h1 style="margin: 0;">📊 Resumen Semanal de Precios</h1>
                    <p style="margin: 10px 0 0 0; opacity: 0.9;">Semana del 28 Enero al 3 Febrero 2026</p>
                </div>

                <div style="background: #f9fafb; padding: 40px; border-radius: 0 0 8px 8px;">
                    <h2 style="color: #111827; margin-top: 0;">⛽ Combustibles</h2>
                    <div style="background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                            <span style="font-weight: bold;">Nafta Premium</span>
                            <span style="color: #ef4444;">$62.50</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; color: #6b7280; font-size: 14px;">
                            <span>Cambio en 7 días</span>
                            <span style="color: #ef4444;">+2.3%</span>
                        </div>
                    </div>

                    <h2 style="color: #111827;">⚡ Servicios Públicos</h2>
                    <div style="background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 15px;">
                            <div>
                                <div style="font-weight: bold;">UTE (Electricidad)</div>
                                <div style="color: #6b7280; font-size: 14px;">Tarifa residencial</div>
                            </div>
                            <span style="color: #f59e0b;">$8.50/kWh</span>
                        </div>
                        <div style="display: flex; justify-content: space-between;">
                            <div>
                                <div style="font-weight: bold;">OSE (Agua)</div>
                                <div style="color: #6b7280; font-size: 14px;">Tarifa residencial</div>
                            </div>
                            <span style="color: #3b82f6;">$47.60/m³</span>
                        </div>
                    </div>

                    <div style="background: #f0fdf4; padding: 15px; border-left: 4px solid #22c55e; margin-bottom: 30px; border-radius: 4px;">
                        <strong style="color: #166534;">💡 Consejo:</strong>
                        <p style="margin: 5px 0 0 0; color: #166534; font-size: 14px;">Los precios de combustibles suben 2.3% esta semana. Considerá cargar el tanque antes de viernes.</p>
                    </div>

                    <div style="text-align: center;">
                        <a href="https://cuantocuestauruguay.com" style="background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 6px; display: inline-block;">
                            Ver más precios →
                        </a>
                    </div>

                    <hr style="border: none; border-top: 1px solid #e5e7eb; margin-top: 30px; margin-bottom: 20px;">

                    <p style="color: #6b7280; font-size: 12px; text-align: center; margin: 0;">
                        Recibiste este email porque te suscribiste a PreciosRegulados.uy<br>
                        <a href="https://cuantocuestauruguay.com/contacto" style="color: #667eea; text-decoration: none;">Desuscribirse</a>
                    </p>
                </div>
            </body>
        </html>
        """

    def get_stats(self) -> dict:
        """Obtener estadísticas del newsletter"""
        with open(SUBSCRIBERS_FILE, "r") as f:
            data = json.load(f)

        subscribers = data.get("subscribers", [])
        active = sum(1 for s in subscribers if s.get("active", True))

        return {
            "total_subscribers": len(subscribers),
            "active_subscribers": active,
            "inactive": len(subscribers) - active,
            "file_location": SUBSCRIBERS_FILE,
        }


def demo():
    """Demo de newsletter"""
    mgr = NewsletterManager()

    print("=" * 80)
    print("📧 Newsletter Manager - Demo")
    print("=" * 80)
    print()

    # Subscribe
    print("1️⃣ Suscribiendo usuarios...")
    mgr.subscribe("usuario1@example.com", "Juan")
    mgr.subscribe("usuario2@example.com", "María")
    mgr.subscribe("usuario3@example.com", "Carlos")
    print("   ✅ 3 usuarios suscritos")
    print()

    # Stats
    print("2️⃣ Estadísticas:")
    stats = mgr.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    print()

    # Send digest
    print("3️⃣ Enviando digest semanal...")
    result = mgr.send_weekly_digest()
    for key, value in result.items():
        print(f"   {key}: {value}")
    print()

    print("✅ Demo completado")


if __name__ == "__main__":
    demo()
