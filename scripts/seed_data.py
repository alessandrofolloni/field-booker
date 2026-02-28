
import asyncio
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from geoalchemy2.elements import WKTElement

# Import models
# We need to add services to path to allow these imports
import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'services'))

from shared.database import AsyncSessionFactory, init_db
from fields.app.models import Sport, Field, FieldSport

async def seed_data():
    print("🏟️  Seeding database with example data...")
    
    # Initialize tables
    await init_db()
    
    async with AsyncSessionFactory() as session:
        # 1. Create Sports
        sports_data = [
            {"name": "Calcio", "icon": "⚽", "color": "#4CAF50"},
            {"name": "Tennis", "icon": "🎾", "color": "#CDDC39"},
            {"name": "Basket", "icon": "🏀", "color": "#FF9800"},
            {"name": "Padel", "icon": "🥎", "color": "#2196F3"},
            {"name": "Pallavolo", "icon": "🏐", "color": "#FFEB3B"},
        ]
        
        sports_map = {}
        for s_info in sports_data:
            # Check if sport exists
            result = await session.execute(select(Sport).filter_by(name=s_info["name"]))
            sport = result.scalar_one_or_none()
            
            if not sport:
                sport = Sport(**s_info)
                session.add(sport)
                print(f"✅ Created sport: {s_info['name']}")
            
            sports_map[s_info["name"]] = sport
            
        await session.commit()
        
        # 2. Create Fields — 30 fields across Italy
        fields_data = [
            # ── MILANO ──────────────────────────────────────────────────────────
            {
                "name": "Centro Sportivo Saini",
                "description": "Grande centro polifunzionale con campi da calcio in erba naturale, atletica e tennis. Strutture di alto livello con spogliatoi, bar e parcheggio gratuito.",
                "lat": 45.4740, "lng": 9.2550,
                "address": "Via Corelli, 136", "city": "Milano",
                "phone": "02 7562 741",
                "email": "info@centrosportivosaini.it",
                "website": "https://www.centrosportivosaini.it",
                "booking_url": "https://www.centrosportivosaini.it/prenota",
                "price_info": "Calcio a 11: 80€/h · Calcio a 7: 60€/h · Tennis: 15€/h",
                "opening_hours": {
                    "lun": "08:00–22:00", "mar": "08:00–22:00", "mer": "08:00–22:00",
                    "gio": "08:00–22:00", "ven": "08:00–22:00",
                    "sab": "08:00–21:00", "dom": "09:00–19:00"
                },
                "sports": ["Calcio", "Tennis"],
                "reviews": [
                    {"rating": 5, "comment": "Campi in ottime condizioni, spogliatoi puliti. Personale molto disponibile."},
                    {"rating": 4, "comment": "Ottima struttura, prezzi nella media. Consiglio di prenotare con anticipo."},
                    {"rating": 5, "comment": "Il campo in erba naturale è semplicemente perfetto. Ci torno sempre!"},
                ]
            },
            {
                "name": "Padel Club Milano Est",
                "description": "6 campi da padel indoor di ultima generazione con illuminazione LED, riscaldamento, spogliatoi con sauna e pro shop. Maestri certificati FIT disponibili.",
                "lat": 45.4510, "lng": 9.1670,
                "address": "Via dei Ciclamini, 18", "city": "Milano",
                "phone": "02 1234 567",
                "email": "prenotazioni@padelclubmilano.it",
                "website": "https://www.padelclubmilano.it",
                "booking_url": "https://playtomic.io/padel-club-milano",
                "price_info": "Ore diurne: 40€/90min · Ore serali: 60€/90min · Lezione maestro: +25€",
                "opening_hours": {
                    "lun": "07:00–23:00", "mar": "07:00–23:00", "mer": "07:00–23:00",
                    "gio": "07:00–23:00", "ven": "07:00–23:00",
                    "sab": "08:00–22:00", "dom": "08:00–21:00"
                },
                "sports": ["Padel"],
                "reviews": [
                    {"rating": 5, "comment": "I migliori campi di padel a Milano. Superficie veloce, luci perfette."},
                    {"rating": 4, "comment": "Struttura fantastica, solo un po' cara nelle ore serali. Ma ne vale la pena."},
                    {"rating": 5, "comment": "Il maestro Marco è bravissimo! Lezione molto utile per migliorare il rovescio."},
                    {"rating": 4, "comment": "Prenotazione online semplicissima. Spogliatoi sempre puliti."},
                ]
            },
            {
                "name": "Oratorio San Barnaba",
                "description": "Campo da calcio a 7 in erba sintetica di ultima generazione, canestro da basket e campo da pallavolo. Aperto a tutti, gestito dai volontari dell'oratorio. Torneo estivo gratuito per ragazzi.",
                "lat": 45.4410, "lng": 9.2010,
                "address": "Via Lodovico Montegani, 12", "city": "Milano",
                "phone": "02 5810 4321",
                "email": "oratorio@sanbarnaba.it",
                "price_info": "Calcio a 7: 30€/h · Basket/Pallavolo: gratuito",
                "opening_hours": {
                    "lun": "15:00–21:00", "mar": "15:00–21:00", "mer": "15:00–21:00",
                    "gio": "15:00–21:00", "ven": "15:00–22:00",
                    "sab": "09:00–22:00", "dom": "10:00–20:00"
                },
                "sports": ["Calcio", "Basket", "Pallavolo"],
                "reviews": [
                    {"rating": 5, "comment": "Posto meraviglioso, prezzi onestissimi. Perfetto per la partitella tra amici."},
                    {"rating": 4, "comment": "Campo in buone condizioni, personale simpatico. Spogliatoi un po' datati."},
                ]
            },
            {
                "name": "Arena Civica Gianni Brera",
                "description": "Storico impianto neoclassico nel cuore di Milano, nel Parco Sempione. Campo da calcio in erba naturale, pista di atletica e tribuna coperta da 6.000 posti. Meta iconica per ogni calciatore milanese.",
                "lat": 45.4748, "lng": 9.1788,
                "address": "Viale Giorgio Byron, 2", "city": "Milano",
                "phone": "02 318 3440",
                "email": "arenacivica@comune.milano.it",
                "website": "https://www.arenacivica.it",
                "price_info": "Calcio a 11: 120€/h · Atletica: 10€/persona/sessione",
                "opening_hours": {
                    "lun": "09:00–21:00", "mar": "09:00–21:00", "mer": "09:00–21:00",
                    "gio": "09:00–21:00", "ven": "09:00–21:00",
                    "sab": "09:00–19:00", "dom": "Chiuso"
                },
                "sports": ["Calcio", "Pallavolo"],
                "reviews": [
                    {"rating": 5, "comment": "Giocare qui è un'emozione unica. Il campo è in condizioni perfette."},
                    {"rating": 4, "comment": "Location storica incredibile. Prenotazione un po' macchinosa ma ne vale la pena."},
                    {"rating": 5, "comment": "Il miglior campo di Milano per atmosfera. Ci ho giocato a 6 anni e ci gioco ancora!"},
                ]
            },
            {
                "name": "Tennis Club Milano Bonacossa",
                "description": "Fondato nel 1920, uno dei più antichi e prestigiosi club di tennis in Italia. 15 campi in terra rossa all'aperto, 4 indoor con illuminazione professionale. Scuola tennis per tutti i livelli, tornei regionali e internazionali.",
                "lat": 45.4850, "lng": 9.1500,
                "address": "Via Giuseppe Arimondi, 15", "city": "Milano",
                "phone": "02 3313 3820",
                "email": "segreteria@tcbonacossa.it",
                "website": "https://www.tcbonacossa.it",
                "booking_url": "https://www.tcbonacossa.it/prenotazioni",
                "price_info": "Terra rossa outdoor: 20€/h · Indoor: 30€/h · Lezione maestro: +35€/h",
                "opening_hours": {
                    "lun": "08:00–22:00", "mar": "08:00–22:00", "mer": "08:00–22:00",
                    "gio": "08:00–22:00", "ven": "08:00–22:00",
                    "sab": "08:00–21:00", "dom": "08:00–20:00"
                },
                "sports": ["Tennis"],
                "reviews": [
                    {"rating": 5, "comment": "Il club più bello di Milano. Terra rossa perfettamente mantenuta, personale impeccabile."},
                    {"rating": 5, "comment": "Ambiente signorile, campi di altissima qualità. La lezione con il maestro Rossi è eccellente."},
                    {"rating": 4, "comment": "Ottimo club, prezzi un po' alti ma la qualità è indiscutibile."},
                ]
            },
            {
                "name": "Palalido Allianz Cloud",
                "description": "Impianto polifunzionale da 5.000 posti nel quartiere Fiera. Sede di eventi sportivi internazionali, concerti e fiere. Disponibile per allenamenti di basket e pallavolo nelle ore non occupate da eventi.",
                "lat": 45.4769, "lng": 9.1462,
                "address": "Piazzale Carlo Stuparich, 1", "city": "Milano",
                "phone": "02 3341 5600",
                "email": "booking@allianzcloud.it",
                "website": "https://www.allianzcloud.it",
                "booking_url": "https://www.allianzcloud.it/noleggio",
                "price_info": "Basket/Pallavolo: da 150€/h (contattare per disponibilità)",
                "opening_hours": {
                    "lun": "Su prenotazione", "mar": "Su prenotazione", "mer": "Su prenotazione",
                    "gio": "Su prenotazione", "ven": "Su prenotazione",
                    "sab": "Su prenotazione", "dom": "Su prenotazione"
                },
                "sports": ["Basket", "Pallavolo"],
                "reviews": [
                    {"rating": 5, "comment": "Parquet professionale NBA-level. Un sogno giocare qui."},
                    {"rating": 4, "comment": "Struttura di livello altissimo. Solo i prezzi sono importanti."},
                ]
            },
            {
                "name": "Beach Town Milano",
                "description": "Il primo beach volley club indoor di Milano con 4 campi in sabbia certificata, riscaldati tutto l'anno. Bar panoramico, area relax, torneo settimanale misto e scuola beach volley.",
                "lat": 45.4100, "lng": 9.1400,
                "address": "Via Bruno Cassinari, 12", "city": "Assago",
                "phone": "02 4550 1234",
                "email": "info@beachtownmilano.it",
                "website": "https://www.beachtownmilano.it",
                "booking_url": "https://www.beachtownmilano.it/prenota",
                "price_info": "Ore diurne: 25€/h · Ore serali: 35€/h · Torneo settimanale: 10€/persona",
                "opening_hours": {
                    "lun": "10:00–23:00", "mar": "10:00–23:00", "mer": "10:00–23:00",
                    "gio": "10:00–23:00", "ven": "10:00–24:00",
                    "sab": "09:00–24:00", "dom": "09:00–22:00"
                },
                "sports": ["Pallavolo"],
                "reviews": [
                    {"rating": 5, "comment": "Atmosfera fantastica! La sabbia è morbidissima e il bar fa ottimi aperitivi."},
                    {"rating": 5, "comment": "Il torneo del giovedì sera è un must. Livello medio-alto, molto divertente."},
                    {"rating": 4, "comment": "Struttura unica a Milano. Sabbia ottima, un po' caldo d'estate anche all'interno."},
                ]
            },
            {
                "name": "Padel It Milano Rogoredo",
                "description": "Centro padel con 8 campi indoor panoramici e 4 outdoor. Bar con vista sui campi, pro shop con le migliori marche, tornei mensili e maestri certificati FIP. Parcheggio gratuito.",
                "lat": 45.4370, "lng": 9.2260,
                "address": "Via Vittorini, 6", "city": "Milano",
                "phone": "02 5839 4567",
                "email": "info@padelit-rogoredo.it",
                "booking_url": "https://playtomic.io/padel-it-rogoredo",
                "price_info": "Mattina/Pomeriggio: 35€/90min · Sera: 55€/90min · Weekend: 60€/90min",
                "opening_hours": {
                    "lun": "07:00–23:00", "mar": "07:00–23:00", "mer": "07:00–23:00",
                    "gio": "07:00–23:00", "ven": "07:00–23:00",
                    "sab": "07:00–23:00", "dom": "08:00–22:00"
                },
                "sports": ["Padel"],
                "reviews": [
                    {"rating": 5, "comment": "I campi outdoor sono fantastici d'estate. Superficie ottima e luci perfette anche di notte."},
                    {"rating": 4, "comment": "Ottima struttura, app di prenotazione intuitiva. A volte un po' affollato il weekend."},
                    {"rating": 5, "comment": "Il maestro è bravissimo. Ho migliorato tantissimo dopo 5 lezioni."},
                ]
            },
            # ── ROMA ────────────────────────────────────────────────────────────
            {
                "name": "Circolo Tennis Parioli",
                "description": "Club storico fondato nel 1950 nel quartiere Parioli. 15 campi in terra rossa all'aperto e 6 campi indoor. Piscina olimpionica, ristorante e bar. Sede di tornei regionali FIT.",
                "lat": 41.9220, "lng": 12.5050,
                "address": "Via Salaria, 62", "city": "Roma",
                "phone": "06 844 0010",
                "email": "info@ctparioli.it",
                "website": "https://www.ctparioli.it",
                "booking_url": "https://www.ctparioli.it/prenota",
                "price_info": "Soci: 25€/h · Ospiti: 40€/h · Indoor: +10€/h",
                "opening_hours": {
                    "lun": "08:00–22:00", "mar": "08:00–22:00", "mer": "08:00–22:00",
                    "gio": "08:00–22:00", "ven": "08:00–22:00",
                    "sab": "08:00–21:00", "dom": "08:00–20:00"
                },
                "sports": ["Tennis"],
                "reviews": [
                    {"rating": 5, "comment": "Il miglior circolo di Roma. Terra rossa perfetta, ambiente esclusivo."},
                    {"rating": 5, "comment": "Campi in ottime condizioni, personale professionale. Il ristorante è ottimo!"},
                    {"rating": 4, "comment": "Qualità altissima, solo un po' difficile prenotare nei weekend."},
                ]
            },
            {
                "name": "Foro Italico — Campi pubblici",
                "description": "Il complesso sportivo olimpico più iconico d'Italia. Campi da tennis in terra rossa dove si giocano gli Internazionali BNL d'Italia, campo da calcio e pista di atletica. Patrimonio dello sport italiano dal 1928.",
                "lat": 41.9330, "lng": 12.4640,
                "address": "Viale dei Gladiatori, 31", "city": "Roma",
                "phone": "06 3685 8218",
                "email": "campi@foro-italico.it",
                "website": "https://www.federtennis.it",
                "price_info": "Tennis: 10€/h campo pubblico · Calcio: 80€/h",
                "opening_hours": {
                    "lun": "08:00–21:00", "mar": "08:00–21:00", "mer": "08:00–21:00",
                    "gio": "08:00–21:00", "ven": "08:00–21:00",
                    "sab": "08:00–20:00", "dom": "08:00–18:00"
                },
                "sports": ["Tennis", "Calcio"],
                "reviews": [
                    {"rating": 5, "comment": "Giocare dove giocano Sinner e Berrettini è un'emozione indescrivibile!"},
                    {"rating": 4, "comment": "Campi in ottimo stato, prezzi accessibili per il livello della struttura."},
                    {"rating": 5, "comment": "Location storica unica. Il lungofiume è bellissimo per il riscaldamento."},
                ]
            },
            {
                "name": "Campo da Calcio Pigneto",
                "description": "Moderno centro sportivo nel quartiere Pigneto con campi da calcio a 5 e a 7 in erba sintetica omologata FIFA Quality. Spogliatoi con docce, tribuna e parcheggio gratuito.",
                "lat": 41.8900, "lng": 12.5400,
                "address": "Via Prenestina, 420", "city": "Roma",
                "phone": "06 2328 7890",
                "email": "info@campipigneto.it",
                "booking_url": "https://www.campipigneto.it",
                "price_info": "Calcio a 5: 60€/h · Calcio a 7: 80€/h · Calcio a 11: 100€/h",
                "opening_hours": {
                    "lun": "09:00–23:00", "mar": "09:00–23:00", "mer": "09:00–23:00",
                    "gio": "09:00–23:00", "ven": "09:00–23:00",
                    "sab": "09:00–23:00", "dom": "09:00–22:00"
                },
                "sports": ["Calcio"],
                "reviews": [
                    {"rating": 4, "comment": "Erba sintetica di qualità, ben mantenuta. Spogliatoi puliti e spaziosi."},
                    {"rating": 5, "comment": "Il campo a 7 è perfetto. Prenotazione online rapidissima."},
                    {"rating": 4, "comment": "Ottima struttura nel quartiere. Prezzi nella media romana."},
                ]
            },
            {
                "name": "Padel Roma Eur",
                "description": "Il più grande centro padel di Roma con 10 campi indoor panoramici nell'elegante quartiere EUR. Pro shop con le migliori marche, bar con aperitivo, tornei settimanali e maestri FIP certificati.",
                "lat": 41.8290, "lng": 12.4710,
                "address": "Viale America, 70", "city": "Roma",
                "phone": "06 5912 3456",
                "email": "info@padeleur.it",
                "booking_url": "https://playtomic.io/padel-roma-eur",
                "price_info": "Mattina: 45€/90min · Sera: 65€/90min · Weekend: 70€/90min",
                "opening_hours": {
                    "lun": "07:00–23:00", "mar": "07:00–23:00", "mer": "07:00–23:00",
                    "gio": "07:00–23:00", "ven": "07:00–23:00",
                    "sab": "07:00–23:00", "dom": "08:00–22:00"
                },
                "sports": ["Padel"],
                "reviews": [
                    {"rating": 5, "comment": "Il miglior centro padel di Roma senza dubbio. Campi veloci, struttura top."},
                    {"rating": 4, "comment": "Ottimo overall. L'aperitivo post partita è un must!"},
                    {"rating": 5, "comment": "Torneo del martedì sera fantastico. Livello medio-alto, molto competitivo."},
                ]
            },
            {
                "name": "Basket City Roma Tor Vergata",
                "description": "Palestra universitaria con 3 campi da basket regolamentari, parquet di qualità professionale. Minibasket per bambini 6–12 anni, corsi per adulti e campionati UISP. Aperto anche agli esterni.",
                "lat": 41.8560, "lng": 12.6010,
                "address": "Via Columbia, 1", "city": "Roma",
                "phone": "06 7259 6000",
                "email": "cus@uniroma2.it",
                "price_info": "Campo intero: 15€/h · Mezza campagna: 8€/h · Tesseramento CUS: 40€/anno",
                "opening_hours": {
                    "lun": "09:00–22:00", "mar": "09:00–22:00", "mer": "09:00–22:00",
                    "gio": "09:00–22:00", "ven": "09:00–21:00",
                    "sab": "09:00–18:00", "dom": "Chiuso"
                },
                "sports": ["Basket", "Pallavolo"],
                "reviews": [
                    {"rating": 4, "comment": "Parquet ottimo, prezzi imbattibili. Ideale per chi abita in zona."},
                    {"rating": 5, "comment": "I corsi di minibasket sono eccellenti. Mio figlio migliora ogni settimana!"},
                ]
            },
            # ── TORINO ──────────────────────────────────────────────────────────
            {
                "name": "Circolo della Stampa Sporting",
                "description": "Elegante club sportivo con 10 campi da tennis in terra rossa, 4 indoor, padel e piscina.",
                "lat": 45.0700, "lng": 7.6780,
                "address": "Corso Giovanni Lanza, 106", "city": "Torino",
                "website": "https://www.circolostampa.it",
                "price_info": "Tennis: 18€/h · Padel: 40€/ora e mezza",
                "sports": ["Tennis", "Padel"]
            },
            {
                "name": "Campo Calcio San Paolo Torino",
                "description": "Campo in erba sintetica a 11 nel quartiere San Paolo. Illuminazione notturna e spogliatoi.",
                "lat": 45.0540, "lng": 7.6580,
                "address": "Via Avigliana, 24", "city": "Torino",
                "phone": "011 318 7651",
                "price_info": "90€/h",
                "sports": ["Calcio"]
            },
            {
                "name": "Palazzetto dello Sport Torino",
                "description": "Struttura polifunzionale per basket e pallavolo. Sede delle partite casalinghe della Reale Mutua Basket.",
                "lat": 45.0670, "lng": 7.6910,
                "address": "Corso Sebastopoli, 123", "city": "Torino",
                "price_info": "Su prenotazione",
                "sports": ["Basket", "Pallavolo"]
            },
            # ── NAPOLI ──────────────────────────────────────────────────────────
            {
                "name": "Centro Sportivo Baia Domizia",
                "description": "Campi da calcio a 5, 7 e 11 sul lungomare. Vista mare e strutture moderne.",
                "lat": 40.8580, "lng": 14.2710,
                "address": "Via Caracciolo, 20", "city": "Napoli",
                "price_info": "Calcio a 5: 50€/h",
                "sports": ["Calcio"]
            },
            {
                "name": "Tennis Napoli Vomero",
                "description": "6 campi in terra rossa nel quartiere collinare Vomero. Scuola tennis per adulti e bambini.",
                "lat": 40.8480, "lng": 14.2280,
                "address": "Via Tasso, 150", "city": "Napoli",
                "phone": "081 556 3412",
                "price_info": "12€/h",
                "sports": ["Tennis"]
            },
            {
                "name": "Padel Napoli Est",
                "description": "Nuovo centro padel con 6 campi indoor. Parcheggio gratuito e bar con vista sui campi.",
                "lat": 40.8640, "lng": 14.3120,
                "address": "Via Argine, 460", "city": "Napoli",
                "booking_url": "https://playtomic.io/padel-napoli-est",
                "price_info": "38€ – 50€ per ora e mezza",
                "sports": ["Padel"]
            },
            # ── BOLOGNA ─────────────────────────────────────────────────────────
            {
                "name": "Virtus Bologna Arena",
                "description": "L'Unipol Arena, casa della Virtus Segafredo Bologna. Disponibile per eventi e allenamenti.",
                "lat": 44.5240, "lng": 11.2760,
                "address": "Via Gino Cervi, 2", "city": "Casalecchio di Reno (BO)",
                "website": "https://www.unipolarena.it",
                "price_info": "Su richiesta",
                "sports": ["Basket"]
            },
            {
                "name": "Tennis Club Bologna",
                "description": "30 campi tra terra rossa e sintetico, indoor e outdoor. Sede di tornei ITF e ATP Challenger.",
                "lat": 44.4960, "lng": 11.3490,
                "address": "Via Murri, 9", "city": "Bologna",
                "website": "https://www.tcbologna.it",
                "price_info": "15€/h outdoor · 28€/h indoor",
                "sports": ["Tennis"]
            },
            {
                "name": "Campi da Calcio Arcoveggio",
                "description": "4 campi in erba sintetica nel Parco dell'Arcoveggio. Il più grande polo calcistico di Bologna.",
                "lat": 44.5210, "lng": 11.3440,
                "address": "Via Arcoveggio, 49", "city": "Bologna",
                "phone": "051 634 7890",
                "price_info": "Calcio a 5: 55€/h · Calcio a 7: 75€/h",
                "sports": ["Calcio"]
            },
            # ── FIRENZE ─────────────────────────────────────────────────────────
            {
                "name": "Assi Giglio Rosso Firenze",
                "description": "Storico circolo sportivo con tennis, padel e calcio. Nel cuore di Firenze con ampio parcheggio.",
                "lat": 43.7800, "lng": 11.2550,
                "address": "Viale Michelangelo, 64", "city": "Firenze",
                "website": "https://www.assigigliorosso.it",
                "price_info": "Tennis: 14€/h · Padel: 38€/ora e mezza",
                "sports": ["Tennis", "Padel", "Calcio"]
            },
            {
                "name": "Palazzetto dello Sport Firenze",
                "description": "Il celebre PalaMandela, capolavoro architettonico di Nervi. Basket e pallavolo ad alto livello.",
                "lat": 43.7720, "lng": 11.2200,
                "address": "Via Paoli, 3", "city": "Firenze",
                "price_info": "Su prenotazione",
                "sports": ["Basket", "Pallavolo"]
            },
            # ── GENOVA ──────────────────────────────────────────────────────────
            {
                "name": "Centro Sportivo Fontanegli",
                "description": "Impianto multidisciplinare in collina con campi da calcio, tennis e padel. Panorama mozzafiato.",
                "lat": 44.4310, "lng": 8.9870,
                "address": "Via Fontanegli, 38", "city": "Genova",
                "phone": "010 831 2210",
                "price_info": "Calcio: 70€/h · Tennis: 12€/h",
                "sports": ["Calcio", "Tennis", "Padel"]
            },
            # ── VERONA ──────────────────────────────────────────────────────────
            {
                "name": "Campi da Padel Verona Nord",
                "description": "8 campi da padel indoor con alta tecnologia. Maestri professionisti e tornei mensili.",
                "lat": 45.4580, "lng": 10.9920,
                "address": "Via Unità d'Italia, 33", "city": "Verona",
                "booking_url": "https://playtomic.io/padel-verona-nord",
                "price_info": "40€ – 55€ per ora e mezza",
                "sports": ["Padel"]
            },
            {
                "name": "Tennis Scaligero Verona",
                "description": "Club affiliato FIT con 12 campi in terra rossa. Tornei Open e scuola tennis a tutti i livelli.",
                "lat": 45.4400, "lng": 10.9710,
                "address": "Lungadige Galtarossa, 21", "city": "Verona",
                "price_info": "12€/h",
                "sports": ["Tennis"]
            },
            # ── PALERMO ─────────────────────────────────────────────────────────
            {
                "name": "Centro Sportivo Sperone",
                "description": "Polo sportivo di quartiere con campi da calcio, basket e pallavolo. Attività per giovani e adulti.",
                "lat": 38.1030, "lng": 13.3850,
                "address": "Via dello Sperone, 60", "city": "Palermo",
                "phone": "091 612 3456",
                "price_info": "Calcio: 40€/h",
                "sports": ["Calcio", "Basket", "Pallavolo"]
            },
            {
                "name": "Padel Palermo Mondello",
                "description": "4 campi da padel a 200 metri dalla spiaggia di Mondello. Aperti fino alle 23. Bar incluso.",
                "lat": 38.2180, "lng": 13.3350,
                "address": "Viale Margherita di Savoia, 52", "city": "Palermo",
                "booking_url": "https://playtomic.io/padel-mondello",
                "price_info": "35€ per ora e mezza",
                "sports": ["Padel"]
            },
            # ── REGGIO EMILIA / MODENA ───────────────────────────────────────────
            {
                "name": "Mapei Stadium",
                "description": "Stadio polifunzionale, casa del Sassuolo Calcio. Omologato per calcio a 11 e atletica leggera.",
                "lat": 44.7145, "lng": 10.6486,
                "address": "Piazzale Atleti Azzurri d'Italia, 1", "city": "Reggio Emilia",
                "website": "https://www.mapeistadium.it",
                "price_info": "Su richiesta",
                "sports": ["Calcio"]
            },
            {
                "name": "PalaPanini Modena",
                "description": "Il tempio della pallavolo italiana. Casa della Modena Volley e della Pallacanestro Tricolore.",
                "lat": 44.6450, "lng": 10.9500,
                "address": "Viale dello Sport, 25", "city": "Modena",
                "website": "https://www.palapanini.it",
                "price_info": "Su prenotazione",
                "sports": ["Pallavolo", "Basket"]
            },
        ]
        
        from sqlalchemy import delete
        from fields.app.models import FieldSport, Review

        for f_info in fields_data:
            # Check if field exists
            result = await session.execute(select(Field).filter_by(name=f_info["name"]))
            field = result.scalar_one_or_none()

            # Create geometry: POINT(longitude latitude)
            point = WKTElement(f'POINT({f_info["lng"]} {f_info["lat"]})', srid=4326)

            if not field:
                field = Field(
                    name=f_info["name"],
                    description=f_info["description"],
                    location=point,
                    address=f_info["address"],
                    city=f_info["city"],
                    phone=f_info.get("phone"),
                    email=f_info.get("email"),
                    website=f_info.get("website"),
                    booking_url=f_info.get("booking_url"),
                    price_info=f_info.get("price_info"),
                    opening_hours=f_info.get("opening_hours", {}),
                    photos=f_info.get("photos", []),
                )
                session.add(field)
                await session.flush()  # Get ID
                print(f"✅ Created field: {f_info['name']} ({f_info['city']})")
            else:
                field.description = f_info["description"]
                field.location = point
                field.address = f_info["address"]
                field.city = f_info["city"]
                field.phone = f_info.get("phone")
                field.email = f_info.get("email")
                field.website = f_info.get("website")
                field.booking_url = f_info.get("booking_url")
                field.price_info = f_info.get("price_info")
                field.opening_hours = f_info.get("opening_hours", {})
                field.photos = f_info.get("photos", [])
                print(f"🔄 Updated field: {f_info['name']} ({f_info['city']})")

            # Update sports (clear and re-add)
            await session.execute(delete(FieldSport).filter_by(field_id=field.id))
            for sport_name in f_info["sports"]:
                if sport_name in sports_map:
                    fs = FieldSport(field_id=field.id, sport_id=sports_map[sport_name].id)
                    session.add(fs)

            # Seed reviews if provided (only add if none exist yet)
            reviews_existing = await session.execute(
                select(Review).filter_by(field_id=field.id)
            )
            if not reviews_existing.scalars().first():
                for rev in f_info.get("reviews", []):
                    session.add(Review(
                        field_id=field.id,
                        user_id=uuid.uuid4(),  # synthetic user
                        rating=rev["rating"],
                        comment=rev["comment"],
                    ))

        await session.commit()
        print(f"\n✨ Seeding completed! {len(fields_data)} fields across Italy.")

if __name__ == "__main__":
    asyncio.run(seed_data())
