
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
                "description": "Grande centro polifunzionale con campi da calcio in erba naturale, atletica e tennis. Strutture di alto livello con spogliatoi e bar.",
                "lat": 45.4740, "lng": 9.2550,
                "address": "Via Corelli, 136", "city": "Milano",
                "phone": "02 7562 741",
                "price_info": "Calcio: 80€/h · Tennis: 15€/h",
                "booking_url": "https://www.centrosportivosaini.it",
                "sports": ["Calcio", "Tennis"]
            },
            {
                "name": "Padel Club Milano Est",
                "description": "6 campi da padel indoor di ultima generazione con illuminazione LED, riscaldamento e spogliatoi con sauna.",
                "lat": 45.4510, "lng": 9.1670,
                "address": "Via dei Ciclamini, 18", "city": "Milano",
                "phone": "02 1234 567",
                "website": "https://www.padelclubmilano.it",
                "booking_url": "https://playtomic.io/padel-club-milano",
                "price_info": "40€ – 60€ per ora e mezza",
                "sports": ["Padel"]
            },
            {
                "name": "Oratorio San Barnaba",
                "description": "Campo da calcio a 7 in erba sintetica, canestro da basket e campo da pallavolo. Aperto a tutti, prezzi popolari.",
                "lat": 45.4410, "lng": 9.2010,
                "address": "Via Lodovico Montegani, 12", "city": "Milano",
                "price_info": "Gratuito o contributo libero",
                "sports": ["Calcio", "Basket", "Pallavolo"]
            },
            {
                "name": "Arena Civica Gianni Brera",
                "description": "Storico impianto nel cuore di Milano con pista di atletica, campo da calcio e tribuna coperta.",
                "lat": 45.4748, "lng": 9.1788,
                "address": "Viale Giorgio Byron, 2", "city": "Milano",
                "phone": "02 318 3440",
                "price_info": "Calcio: 100€/h",
                "sports": ["Calcio", "Pallavolo"]
            },
            {
                "name": "Tennis Club Milano Bonacossa",
                "description": "Uno dei più antichi club di tennis in Italia. 15 campi in terra rossa, 4 indoor. Scuola tennis e tornei.",
                "lat": 45.4850, "lng": 9.1500,
                "address": "Via Giuseppe Arimondi, 15", "city": "Milano",
                "website": "https://www.tcbonacossa.it",
                "price_info": "20€/h terra rossa · 30€/h indoor",
                "sports": ["Tennis"]
            },
            {
                "name": "Palalido Allianz Cloud",
                "description": "Impianto polifunzionale da 5000 posti per basket e pallavolo, sede di eventi sportivi internazionali.",
                "lat": 45.4769, "lng": 9.1462,
                "address": "Piazzale Carlo Stuparich, 1", "city": "Milano",
                "website": "https://www.allianzcloud.it",
                "price_info": "Su richiesta",
                "sports": ["Basket", "Pallavolo"]
            },
            {
                "name": "Beach Town Milano",
                "description": "4 campi da beach volley coperti e riscaldati, bar panoramico e area relax. Aperto tutto l'anno.",
                "lat": 45.4100, "lng": 9.1400,
                "address": "Via Bruno Cassinari, 12", "city": "Assago",
                "website": "https://www.beachtownmilano.it",
                "booking_url": "https://www.beachtownmilano.it/prenota",
                "price_info": "30€/h per campo",
                "sports": ["Pallavolo"]
            },
            {
                "name": "Padel It Milano Rogoredo",
                "description": "Centro padel con 8 campi indoor e 4 outdoor. Bar, pro shop e maestri certificati.",
                "lat": 45.4370, "lng": 9.2260,
                "address": "Via Vittorini, 6", "city": "Milano",
                "booking_url": "https://playtomic.io/padel-it-rogoredo",
                "price_info": "35€ – 55€ per ora e mezza",
                "sports": ["Padel"]
            },
            # ── ROMA ────────────────────────────────────────────────────────────
            {
                "name": "Circolo Tennis Parioli",
                "description": "Club storico nel quartiere Parioli con 15 campi in terra rossa e 6 campi coperti. Piscina e ristorante.",
                "lat": 41.9220, "lng": 12.5050,
                "address": "Largo del Foro Italico, 3", "city": "Roma",
                "website": "https://www.ctparioli.it",
                "price_info": "25€/h soci · 40€/h ospiti",
                "sports": ["Tennis"]
            },
            {
                "name": "Foro Italico — Campi pubblici",
                "description": "Complesso sportivo olimpico con campi da tennis, calcio e atletica. Sede degli Internazionali BNL.",
                "lat": 41.9330, "lng": 12.4640,
                "address": "Viale dei Gladiatori, 31", "city": "Roma",
                "phone": "06 3685 8218",
                "price_info": "Tennis: 10€/h",
                "sports": ["Tennis", "Calcio"]
            },
            {
                "name": "Campo da Calcio Pigneto",
                "description": "Campo da calcio a 5 e a 7 in erba sintetica di ultima generazione. Spogliatoi e parcheggio.",
                "lat": 41.8900, "lng": 12.5400,
                "address": "Via Prenestina, 420", "city": "Roma",
                "phone": "06 2328 7890",
                "booking_url": "https://www.campipigneto.it",
                "price_info": "Calcio a 5: 60€/h · Calcio a 7: 80€/h",
                "sports": ["Calcio"]
            },
            {
                "name": "Padel Roma Eur",
                "description": "10 campi da padel nel cuore dell'EUR. Struttura moderna con pro shop, bar e zona relax.",
                "lat": 41.8290, "lng": 12.4710,
                "address": "Viale America, 70", "city": "Roma",
                "booking_url": "https://playtomic.io/padel-roma-eur",
                "price_info": "45€ – 65€ per ora e mezza",
                "sports": ["Padel"]
            },
            {
                "name": "Basket City Roma Tor Vergata",
                "description": "Palestra con 3 campi da basket regolamentari. Minibasket, corsi e campionati UISP.",
                "lat": 41.8560, "lng": 12.6010,
                "address": "Via Columbia, 1", "city": "Roma",
                "price_info": "15€/h campo intero",
                "sports": ["Basket", "Pallavolo"]
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
                    website=f_info.get("website"),
                    booking_url=f_info.get("booking_url"),
                    price_info=f_info.get("price_info")
                )
                session.add(field)
                await session.flush() # Get ID
                print(f"✅ Created field: {f_info['name']}")
            else:
                # Update existing field
                field.description = f_info["description"]
                field.location = point
                field.address = f_info["address"]
                field.city = f_info["city"]
                field.phone = f_info.get("phone")
                field.website = f_info.get("website")
                field.booking_url = f_info.get("booking_url")
                field.price_info = f_info.get("price_info")
                print(f"🔄 Updated field: {f_info['name']}")
            
            # Update sports (clear and re-add for simplicity in seed)
            from sqlalchemy import delete
            from fields.app.models import FieldSport
            await session.execute(delete(FieldSport).filter_by(field_id=field.id))
            
            for sport_name in f_info["sports"]:
                if sport_name in sports_map:
                    fs = FieldSport(field_id=field.id, sport_id=sports_map[sport_name].id)
                    session.add(fs)
                
        await session.commit()
        print(f"\n✨ Seeding completed! {len(fields_data)} fields across Italy.")

if __name__ == "__main__":
    asyncio.run(seed_data())
