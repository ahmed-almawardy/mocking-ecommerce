import asyncio
from decimal import Decimal

from sqlalchemy import select

from app.db.session import AsyncSessionLocal
from app.models import Offer, Product

PRODUCTS = [
    {"sku":"NH-AC-18K","slug":"nova-inverter-air-conditioner-1-5hp","name":"Inverter Air Conditioner 1.5 HP","category":"Air Conditioners","description":"Efficient cooling with quiet operation, multiple fan modes and a clean modern finish.","price":"24999.00","compare_at_price":"27999.00","stock_qty":18,"badge":"Best seller","featured":True,"image_url":"/images/products/air-conditioner.webp"},
    {"sku":"NH-WM-8KG","slug":"nova-front-load-washing-machine-8kg","name":"Front Load Washing Machine 8 KG","category":"Washing Machines","description":"A generous 8 KG capacity, everyday wash programs and a compact contemporary design.","price":"18499.00","compare_at_price":"20999.00","stock_qty":12,"badge":"Save 12%","featured":True,"image_url":"/images/products/washing-machine.webp"},
    {"sku":"NH-CK-5B","slug":"nova-stainless-gas-cooker-5-burner","name":"Stainless Gas Cooker 5 Burners","category":"Cookers","description":"Five burners, a spacious oven and easy-clean stainless steel styling for family kitchens.","price":"13999.00","compare_at_price":None,"stock_qty":9,"badge":"New","featured":True,"image_url":"/images/products/gas-cooker.webp"},
    {"sku":"NH-FR-420","slug":"nova-no-frost-refrigerator-420l","name":"No Frost Refrigerator 420 L","category":"Cooling Appliances","description":"Spacious storage, balanced cooling and a modern finish designed for busy households.","price":"29999.00","compare_at_price":"32999.00","stock_qty":7,"badge":"Special offer","featured":True,"image_url":"/images/products/refrigerator.webp"},
    {"sku":"NH-TV-55","slug":"nova-smart-tv-55-inch-4k","name":"Smart TV 55 inch 4K UHD","category":"Televisions","description":"A vivid 4K display, smart streaming apps and a slim bezel for a cinematic living room.","price":"21999.00","compare_at_price":None,"stock_qty":15,"badge":"Popular","featured":True,"image_url":"/images/products/television.webp"},
    {"sku":"NH-AF-6L","slug":"nova-digital-air-fryer-6l","name":"Digital Air Fryer 6 L","category":"Small Home Appliances","description":"Large-capacity air frying with easy digital controls and quick-clean cooking accessories.","price":"3499.00","compare_at_price":"3999.00","stock_qty":35,"badge":"Save 500 EGP","featured":False,"image_url":"/images/products/blender.webp"},
    {"sku":"NH-WH-50","slug":"nova-electric-water-heater-50l","name":"Electric Water Heater 50 L","category":"Water Heaters","description":"Dependable hot water with a practical capacity and a simple, durable design.","price":"4799.00","compare_at_price":None,"stock_qty":21,"badge":None,"featured":False,"image_url":"/images/products/air-conditioner.webp"},
    {"sku":"NH-MW-34","slug":"nova-digital-microwave-34l","name":"Digital Microwave 34 L","category":"Small Home Appliances","description":"A versatile microwave with digital controls, multiple power settings and roomy capacity.","price":"5299.00","compare_at_price":"5899.00","stock_qty":16,"badge":"New","featured":False,"image_url":"/images/products/microwave.webp"},
]


async def main():
    async with AsyncSessionLocal() as db:
        for item in PRODUCTS:
            existing = await db.scalar(select(Product).where(Product.sku == item["sku"]))
            values = dict(item)
            values["price"] = Decimal(values["price"])
            values["compare_at_price"] = Decimal(values["compare_at_price"]) if values["compare_at_price"] else None
            if existing:
                # Repair the former placeholder SVG asset paths while preserving
                # any administrator-uploaded/custom image URLs.
                current_image = (existing.image_url or "").lower()
                if not current_image or (current_image.startswith("/images/products/") and current_image.endswith(".svg")):
                    existing.image_url = values["image_url"]
                continue
            db.add(Product(**values))

        offers = [
            {"title":"A little more for your home", "subtitle":"Discover useful appliances and everyday value.", "title_ar":"المزيد من الراحة لمنزلك", "subtitle_ar":"اكتشف أجهزة عملية وقيمة يومية لمنزلك.", "image_url":"/images/offers/offer-1.webp", "badge":"FEATURED", "sort_order":1},
            {"title":"Cooling made comfortable", "subtitle":"Find the right comfort for every room.", "title_ar":"راحة وانتعاش في كل غرفة", "subtitle_ar":"اكتشف حلول التبريد المناسبة لكل غرفة.", "image_url":"/images/offers/offer-2.webp", "badge":"COOLING", "sort_order":2},
            {"title":"Everyday kitchen essentials", "subtitle":"Smart helpers for the heart of your home.", "title_ar":"أساسيات مطبخك اليومية", "subtitle_ar":"أجهزة ذكية تساعدك في قلب منزلك.", "image_url":"/images/offers/offer-3.webp", "badge":"KITCHEN", "sort_order":3},
            {"title":"Better living starts here", "subtitle":"Explore our curated home appliance collection.", "title_ar":"حياة أفضل تبدأ من هنا", "subtitle_ar":"تسوق مجموعتنا المختارة من الأجهزة المنزلية.", "image_url":"/images/offers/offer-4.webp", "badge":"NOVA PICKS", "sort_order":4},
        ]
        for item in offers:
            existing_offer = await db.scalar(select(Offer).where(Offer.title == item["title"]))
            if not existing_offer:
                db.add(Offer(**item, link_url="/en/products", is_active=True))
        await db.commit()
    print(f"Seeded {len(PRODUCTS)} catalog records and four initial offers (existing administrator content was retained).")


if __name__ == "__main__":
    asyncio.run(main())
