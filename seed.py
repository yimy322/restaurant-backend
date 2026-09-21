"""Script para poblar la base de datos SQLite con datos iniciales (Seed).
Crea tablas, categorias, platos peruanos y horarios de atencion de lunes a domingo.
"""

from datetime import time
from sqlmodel import Session, select
from app.database import engine, create_db_and_tables
from app.models import Category, Dish, OpeningHour

def seed_database():
    print("Iniciando la creacion de tablas...")
    create_db_and_tables()
    print("Tablas verificadas/creadas con exito.")

    with Session(engine) as session:
        # 1. Verificar si ya existen categorias para evitar duplicados
        existing_categories = session.exec(select(Category)).all()
        if existing_categories:
            print(f"La base de datos ya contiene {len(existing_categories)} categorias. Omitiendo seed de categorias y platos.")
        else:
            print("Insertando categorias gastronómicas...")
            cat_entradas = Category(name="Entradas")
            cat_fondos = Category(name="Platos de Fondo")
            cat_postres = Category(name="Postres")
            cat_bebidas = Category(name="Bebidas")

            session.add_all([cat_entradas, cat_fondos, cat_postres, cat_bebidas])
            session.commit()
            session.refresh(cat_entradas)
            session.refresh(cat_fondos)
            session.refresh(cat_postres)
            session.refresh(cat_bebidas)
            print("Categorias registradas con exito.")

            print("Insertando platos de la carta peruana...")
            dishes = [
                # Entradas
                Dish(
                    name="Ceviche Clásico",
                    description="Pescado fresco del día marinado en zumo de limón, ají limo, cebolla roja, camote glaseado y choclo desgranado.",
                    price=38.00,
                    category_id=cat_entradas.id,
                    image_url="/img/comidas/ceviche.jpg"
                ),
                Dish(
                    name="Causa Limeña de Pollo",
                    description="Suave masa de papa amarilla sazonada con ají amarillo y limón, rellena de pechuga de pollo deshilachada y palta fuerte.",
                    price=24.00,
                    category_id=cat_entradas.id,
                    image_url="/img/comidas/causa.jpg"
                ),
                Dish(
                    name="Papa a la Huancaína",
                    description="Papas sancochadas bañadas en cremosa salsa huancaína tradicional a base de queso fresco y ají amarillo, con huevo y aceituna.",
                    price=20.00,
                    category_id=cat_entradas.id,
                    image_url="/img/comidas/huancaina.jpg"
                ),
                Dish(
                    name="Anticuchos de Corazón",
                    description="Tres brochetas de corazón de res maceradas en ají panca y especias peruanas, acompañadas de papa dorada y choclo.",
                    price=28.00,
                    category_id=cat_entradas.id,
                    image_url="/img/comidas/anticucho.jpg"
                ),
                # Fondos
                Dish(
                    name="Lomo Saltado Criollo",
                    description="Trozos jugosos de lomo fino salteados al wok con cebolla, tomate, ají amarillo y cilantro, servido con papas fritas crocantes y arroz con choclo.",
                    price=46.00,
                    category_id=cat_fondos.id,
                    image_url="/img/comidas/lomo.png"
                ),
                Dish(
                    name="Ají de Gallina Tradicional",
                    description="Pechuga de gallina deshilachada en crema de ají amarillo, nueces y queso parmesano, servido con arroz blanco y papas amarillas.",
                    price=36.00,
                    category_id=cat_fondos.id,
                    image_url="/img/comidas/aji_de_gallina.png"
                ),
                Dish(
                    name="Arroz con Mariscos",
                    description="Arroz al wok aromatizado con pasta de ají amarillo y vino blanco, con mixtura de mariscos selectos (langostinos, calamares y conchas).",
                    price=48.00,
                    category_id=cat_fondos.id,
                    image_url="/img/comidas/arroz_mariscos.jpg"
                ),
                Dish(
                    name="Seco de Res con Frejoles",
                    description="Guiso tierno de carne de res macerada en chicha de jora y culantro, servido con frejoles cremosos y arroz criollo.",
                    price=42.00,
                    category_id=cat_fondos.id,
                    image_url="/img/comidas/seco_res.webp"
                ),
                # Postres
                Dish(
                    name="Suspiro a la Limeña",
                    description="Clásico manjar blanco a base de yemas de huevo aromatizado con esencia de vainilla, coronado con merengue al oporto y canela.",
                    price=18.00,
                    category_id=cat_postres.id,
                    image_url="/img/comidas/suspiro.png"
                ),
                Dish(
                    name="Mazamorra Morada con Arroz con Leche (Clásico)",
                    description="El tradicional postre bicolor peruano: mazamorra de maíz morado con frutas secas combinada con suave arroz con leche de olla.",
                    price=16.00,
                    category_id=cat_postres.id,
                    image_url="/img/comidas/mazamorra_morada.png"
                ),
                Dish(
                    name="Picarones con Miel de Chancaca",
                    description="Aros crocantes de masa de camote y zapallo bañados en miel artesanal perfumada con naranja, canela y clavo de olor.",
                    price=15.00,
                    category_id=cat_postres.id,
                    image_url="/img/comidas/picarones.jpg"
                ),
                # Bebidas
                Dish(
                    name="Chicha Morada Tradicional (Jarra 1L)",
                    description="Bebida emblemática preparada con maíz morado hervido con piña, manzana, canela y clavo de olor, con toque de limón fresco.",
                    price=18.00,
                    category_id=cat_bebidas.id,
                    image_url="/img/comidas/chicha.jpg"
                ),
                Dish(
                    name="Pisco Sour Quebranta",
                    description="Cóctel bandera peruano elaborado con pisco puro Quebranta, zumo de limón recién exprimido, jarabe de goma y clara de huevo.",
                    price=25.00,
                    category_id=cat_bebidas.id,
                    image_url="/img/comidas/pisco_sour.jpg"
                ),
                Dish(
                    name="Limonada Frozen con Hierba Buena",
                    description="Refrescante limonada granizada con hojas frescas de hierba buena y jarabe artesanal.",
                    price=14.00,
                    category_id=cat_bebidas.id,
                    image_url="/img/comidas/limonada_frozen.png"
                ),
            ]
            session.add_all(dishes)
            session.commit()
            print(f"Se insertaron {len(dishes)} platos exitosamente.")

        # 2. Horarios de atencion (OpeningHour)
        existing_hours = session.exec(select(OpeningHour)).all()
        if existing_hours:
            print(f"Ya existen {len(existing_hours)} registros de horarios de atencion.")
        else:
            print("Insertando horarios de atencion de Lunes a Domingo...")
            hours = [
                OpeningHour(day_of_week="monday", open_time=time(12, 0), close_time=time(22, 30)),
                OpeningHour(day_of_week="tuesday", open_time=time(12, 0), close_time=time(22, 30)),
                OpeningHour(day_of_week="wednesday", open_time=time(12, 0), close_time=time(22, 30)),
                OpeningHour(day_of_week="thursday", open_time=time(12, 0), close_time=time(22, 30)),
                OpeningHour(day_of_week="friday", open_time=time(12, 0), close_time=time(23, 0)),
                OpeningHour(day_of_week="saturday", open_time=time(12, 0), close_time=time(23, 30)),
                OpeningHour(day_of_week="sunday", open_time=time(12, 0), close_time=time(18, 30)),
            ]
            session.add_all(hours)
            session.commit()
            print("Horarios de atencion registrados con exito (7 dias de la semana).")

    print("\n--- BASE DE DATOS POBLADA SATISFACTORIAMENTE ---")

if __name__ == "__main__":
    seed_database()
