from sqlalchemy.orm import Session
from sqlalchemy import or_
import models, schemas

def get_ads(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.AdContent).offset(skip).limit(limit).all()

def get_faq_response(db: Session, message: str):
    # Simple keyword matching for demo purposes
    # In a real app, you might use vector search or just let Gemini handle it
    # This tries to find a FAQ entry where one of the trigger_keywords is in the message
    faqs = db.query(models.FaqResponse).all()
    for faq in faqs:
        if faq.trigger_keywords:
            keywords = faq.trigger_keywords.split(",")
            for kn in keywords:
                if kn.strip() in message:
                    return faq
    return None

def search_ads_by_keyword(db: Session, keyword: str):
    return db.query(models.AdContent).filter(
        or_(
            models.AdContent.shop_name.contains(keyword),
            models.AdContent.description.contains(keyword),
            models.AdContent.category.contains(keyword)
        )
    ).all()

def get_all_ads_text(db: Session) -> str:
    # Helper to get all ads text for RAG context
    ads = get_ads(db)
    text_parts = []
    for ad in ads:
        part = f"Name: {ad.shop_name}, Category: {ad.category}, Info: {ad.description}, Hours: {ad.business_hours}"
        text_parts.append(part)
    return "\n".join(text_parts)
