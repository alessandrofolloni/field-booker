
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
        
        # 2. Create Fields
        fields_data = [
            {
                "name": "Centro Sportivo Saini",
                "description": "Grande centro polifunzionale con campi da calcio, atletica e tennis.",
                "lat": 45.4740,
                "lng": 9.2550,
                "address": "Via Corelli, 136",
                "city": "Milano",
                "phone": "02 7562 741",
                "sports": ["Calcio", "Tennis"]
            },
            {
                "name": "Padel Club Milano",
                "description": "Campi da padel di ultima generazione al coperto con riscaldamento e spogliatoi moderni.",
                "lat": 45.4510,
                "lng": 9.1670,
                "address": "Via dei Ciclamini, 18",
                "city": "Milano",
                "phone": "02 1234 567",
                "website": "https://www.padelclubmilano.it",
                "booking_url": "https://playtomic.io/padel-club-milano",
                "price_info": "40€ - 60€ per ora e mezza",
                "sports": ["Padel"]
            },
            {
                "name": "Oratorio San Barnaba",
                "description": "Campo da calcio a 7 e canestro da basket pubblico.",
                "lat": 45.4410,
                "lng": 9.2010,
                "address": "Via Lodovico Montegani, 12",
                "city": "Milano",
                "sports": ["Calcio", "Basket", "Pallavolo"]
            },
            {
                "name": "Stadio San Siro",
                "description": "La Scala del Calcio.",
                "lat": 45.4781,
                "lng": 9.1240,
                "address": "Piazzale Angelo Moratti",
                "city": "Milano",
                "sports": ["Calcio"]
            },
            {
                "name": "Mapei Stadium",
                "description": "Stadio polifunzionale, casa del Sassuolo.",
                "lat": 44.7145,
                "lng": 10.6486,
                "address": "Piazzale Atleti Azzurri d'Italia, 1",
                "city": "Reggio Emilia",
                "sports": ["Calcio"]
            },
            {
                "name": "Circolo Tennis Reggio",
                "description": "Prestigioso circolo tennis con campi in terra rossa.",
                "lat": 44.6980,
                "lng": 10.6180,
                "address": "Via Victor Hugo, 2",
                "city": "Reggio Emilia",
                "sports": ["Tennis", "Padel"]
            },
            {
                "name": "PalaPanini",
                "description": "Il tempio della pallavolo.",
                "lat": 44.6450,
                "lng": 10.9500,
                "address": "Viale dello Sport, 25",
                "city": "Modena",
                "sports": ["Pallavolo", "Basket"]
            },
            {
                "name": "Oratorio Sant'Agostino",
                "description": "Campo da calcio e basket di quartiere.",
                "lat": 44.6460,
                "lng": 10.6490,
                "address": "Piazzetta Sant'Agostino",
                "city": "Reggio Emilia",
                "sports": ["Calcio", "Basket"]
            },
            {
                "name": "Arena Civica Gianni Brera",
                "description": "Storico impianto nel cuore di Milano.",
                "lat": 45.4748,
                "lng": 9.1788,
                "address": "Viale Giorgio Byron, 2",
                "city": "Milano",
                "sports": ["Calcio", "Pallavolo"]
            },
            {
                "name": "Tennis Club Milano Bonacossa",
                "description": "Uno dei più antichi club di tennis in Italia.",
                "lat": 45.4850,
                "lng": 9.1500,
                "address": "Via Giuseppe Arimondi, 15",
                "city": "Milano",
                "sports": ["Tennis"]
            },
            {
                "name": "Beach Town Milano",
                "description": "Campi da beach volley coperti e riscaldati.",
                "lat": 45.4100,
                "lng": 9.1400,
                "address": "Via Bruno Cassinari, 12",
                "city": "Assago",
                "sports": ["Pallavolo"]
            }
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
        print("\n✨ Seeding completed successfully!")

if __name__ == "__main__":
    asyncio.run(seed_data())
