import os
import pandas as pd
import numpy as np
import joblib
# from decimal import Decimal
from django.conf import settings
from product.models import Product

# Load AI model once when the server starts
MODEL_PATH = os.path.join(settings.BASE_DIR, 'ml_models', 'best_recommender_model.pkl')
recommender_model = joblib.load(MODEL_PATH)

def get_ai_recommendations(cart_products, top_n=5):
    """
    Takes cart products and returns top N recommended products.
    """
    if not cart_products:
        return []

    # --- 1. Get cart info ---
    # Get prices and brand names
    cart_prices = [float(p.final_price) for p in cart_products if p.final_price]
    cart_brands = [p.brand.name for p in cart_products if p.brand]

    # Get main categories (use parent if exists)
    cart_main_cats = []
    for p in cart_products:
        if p.category:
            if p.category.parent:
                cart_main_cats.append(p.category.parent.name)
            else:
                cart_main_cats.append(p.category.name)

    # Stop if no valid prices found
    if not cart_prices:
        return []

    # Calculate cart stats
    cart_items_count = len(cart_products)
    cart_mean_price = float(np.mean(cart_prices))
    cart_max_price = float(np.max(cart_prices))
    cart_min_price = float(np.min(cart_prices))

    # --- 2. Get candidates from DB ---
    # Get IDs of cart items to exclude them
    cart_product_ids = [p.id for p in cart_products]

    # Get 50 random products (optimized with select_related)
    candidates = Product.objects.select_related(
        'brand', 'category', 'category__parent'
    ).exclude(id__in=cart_product_ids).order_by('?')[:50]

    features_list = []
    candidate_objs = []

    # --- 3. Build features for each candidate ---
    for cand in candidates:
        cand_price = float(cand.final_price)

        # Find candidate's main category
        if cand.category:
            cand_main_cat = cand.category.parent.name if cand.category.parent else cand.category.name
        else:
            cand_main_cat = 'unknown'

        # Compare prices
        p_ratio = cand_price / (cart_mean_price + 1e-5)
        p_diff = abs(cand_price - cart_mean_price)

        # Check matching brand or category
        is_same_brand = 1 if (cand.brand and cand.brand.name in cart_brands) else 0
        is_same_main_cat = 1 if cand_main_cat in cart_main_cats else 0

        # Fixed score for now (will be updated later)
        cooc_score = 0.05

        # Save data for the AI model
        features_list.append({
            'cart_items_count': cart_items_count,
            'cart_mean_price': round(cart_mean_price, 2),
            'cart_max_price': round(cart_max_price, 2),
            'cart_min_price': round(cart_min_price, 2),
            'candidate_price': round(cand_price, 2),
            'price_ratio': round(p_ratio, 4),
            'price_diff': round(p_diff, 2),
            'is_same_brand': is_same_brand,
            'is_same_main_category': is_same_main_cat,
            'category_cooccurrence_score': cooc_score
        })
        candidate_objs.append(cand)

    if not features_list:
        return []

    # --- 4. AI Prediction ---
    df_features = pd.DataFrame(features_list)

    # Get probabilities from the AI model (class 1 = will buy)
    probabilities = recommender_model.predict_proba(df_features)[:, 1]

    # --- 5. Sort and return ---
    # Match products with their scores
    scored_candidates = list(zip(candidate_objs, probabilities))

    # Sort by highest score
    scored_candidates.sort(key=lambda x: x[1], reverse=True)

    # Return the top N products
    recommended_products = [item[0] for item in scored_candidates[:top_n]]

    return recommended_products