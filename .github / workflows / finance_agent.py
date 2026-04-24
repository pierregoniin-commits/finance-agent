import anthropic
from twilio.rest import Client
from datetime import datetime
import os

# ─────────────────────────────────────────
# CONFIGURATION — remplace par tes vraies clés
# ─────────────────────────────────────────
ANTHROPIC_API_KEY  = os.environ.get("ANTHROPIC_API_KEY", "sk-ant-...")
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID", "ACxxxxxxxxxxxxxxxx")
TWILIO_AUTH_TOKEN  = os.environ.get("TWILIO_AUTH_TOKEN", "xxxxxxxxxxxxxxxx")
TWILIO_FROM        = "whatsapp:+14155238886"       # Numéro sandbox Twilio (fixe)
WHATSAPP_TO        = os.environ.get("WHATSAPP_TO", "whatsapp:+336XXXXXXXX")  # Ton numéro


# ─────────────────────────────────────────
# ÉTAPE 1 — Appel à l'agent Claude
# ─────────────────────────────────────────
def get_finance_briefing() -> str:
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    today = datetime.now().strftime("%A %d %B %Y")

    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1500,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[
            {
                "role": "user",
                "content": f"""
Tu es un analyste financier senior. Aujourd'hui nous sommes le {today}.

Ta mission : rechercher et synthétiser les 5 actualités financières les plus importantes du jour.

Critères de sélection (par ordre de priorité) :
1. Mouvements majeurs des marchés (CAC 40, S&P 500, Nikkei, taux obligataires)
2. Décisions de banques centrales (BCE, Fed, BoE)
3. Opérations M&A significatives (>500M€)
4. Résultats d'entreprises du CAC 40 / S&P 500
5. Macro-économie (inflation, PIB, emploi)

Format de réponse STRICT (WhatsApp-friendly, max 1500 caractères au total) :

📊 *Briefing Finance — {today}*

1️⃣ [Titre court]
→ [Résumé 2 lignes max] _(Source)_

2️⃣ [Titre court]
→ [Résumé 2 lignes max] _(Source)_

3️⃣ [Titre court]
→ [Résumé 2 lignes max] _(Source)_

4️⃣ [Titre court]
→ [Résumé 2 lignes max] _(Source)_

5️⃣ [Titre court]
→ [Résumé 2 lignes max] _(Source)_

_Généré automatiquement à {datetime.now().strftime("%H:%M")}_

Réponds UNIQUEMENT avec le briefing formaté, rien d'autre.
"""
            }
        ]
    )

    # Extraire le texte de la réponse (Claude peut avoir utilisé web_search)
    full_text = ""
    for block in response.content:
        if block.type == "text":
            full_text += block.text

    return full_text.strip()


# ─────────────────────────────────────────
# ÉTAPE 2 — Envoi sur WhatsApp via Twilio
# ─────────────────────────────────────────
def send_whatsapp(message: str) -> None:
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

    msg = client.messages.create(
        from_=TWILIO_FROM,
        to=WHATSAPP_TO,
        body=message
    )
    print(f"✅ Message envoyé — SID: {msg.sid}")


# ─────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────
if __name__ == "__main__":
    print("🔍 Recherche des actualités financières...")
    briefing = get_finance_briefing()

    print("\n📋 Briefing généré :\n")
    print(briefing)

    print("\n📱 Envoi sur WhatsApp...")
    send_whatsapp(briefing)
