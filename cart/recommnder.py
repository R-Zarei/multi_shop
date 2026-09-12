import os
import json
import pandas as pd
import numpy as np
import joblib
from django.conf import settings
from django.db.models import Q
from product.models import Product

# 1. Load ML model once when the server starts
MODEL_PATH = os.path.join(settings.BASE_DIR, 'ml_models', 'best_recommender_model.pkl')
recommender_model = joblib.load(MODEL_PATH)

# 2. Load Co-occurrence Matrix once
COOC_PATH = os.path.join(settings.BASE_DIR, 'data', 'jsons', 'category_cooc.json')
try:
    with open(COOC_PATH, 'r', encoding='utf-8') as f:
        cooc_matrix = json.load(f)
except FileNotFoundError:
    print(f"Warning: Co-occurrence file not found at {COOC_PATH}. Defaulting to empty matrix.")
    cooc_matrix = {}


def format_category_for_ai(category_obj):
    """
    Converts Django category path (e.g., 'Computers > Camera')
    to dataset format (e.g., 'computers.camera')
    """
    if not category_obj:
        return 'unknown'
    full_path = category_obj.get_full_path()
    return full_path.lower().replace(' > ', '.').replace(' ', '_')


def get_ai_recommendations(cart_products, top_n=5):
    """
    Takes cart products and returns top N recommended products using AI.
    """
    if not cart_products:
        return []

    # --- 1. Get cart info ---
    cart_prices = [float(p.final_price) for p in cart_products if p.final_price]
    cart_brands = [p.brand.name for p in cart_products if p.brand]

    # Get cart categories in AI format (e.g., 'electronics.smartphone')
    cart_cats_ai = [format_category_for_ai(p.category) for p in cart_products if p.category]

    # 🟢 اصلاح اول: گرفتن دسته‌بندی ریشه (Root) برای سبد خرید با کلمه اول
    cart_main_cats = [cat_ai.split('.')[0] for cat_ai in cart_cats_ai]

    if not cart_prices:
        return []

    cart_items_count = len(cart_products)
    cart_mean_price = float(np.mean(cart_prices))
    cart_max_price = float(np.max(cart_prices))
    cart_min_price = float(np.min(cart_prices))

    # --- 2. Smart Candidate Generation (Filtering) ---
    cart_product_ids = [p.id for p in cart_products]
    cart_brand_ids = [p.brand_id for p in cart_products if p.brand_id]

    # 🟢 اصلاح دوم: پیدا کردن ریشه مطلق (بالاترین سطح بدون والد) برای جلوگیری از تداخل دسته‌های میانی
    root_category_ids = set()
    for p in cart_products:
        if p.category:
            root = p.category
            while root.parent_id is not None:
                root = root.parent
            root_category_ids.add(root.id)

    # Build dynamic OR query
    candidate_query = Q()

    if root_category_ids:
        candidate_query |= Q(category_id__in=root_category_ids)
        candidate_query |= Q(category__parent_id__in=root_category_ids)
        candidate_query |= Q(category__parent__parent_id__in=root_category_ids)

    if cart_brand_ids:
        candidate_query |= Q(brand_id__in=cart_brand_ids)

    candidate_query |= Q(discount__isnull=False)

    # Fetch candidate products matching the criteria
    candidates = Product.objects.select_related(
        'brand', 'category', 'category__parent'
    ).filter(candidate_query).exclude(
        id__in=cart_product_ids
    ).distinct().order_by('?')[:100]

    # Fallback to random candidates if filtered pool is too small
    if len(candidates) < 30:
        extra_candidates = Product.objects.select_related(
            'brand', 'category', 'category__parent'
        ).exclude(id__in=cart_product_ids).order_by('?')[:(100 - len(candidates))]
        candidates = list(candidates) + list(extra_candidates)
        candidates = list(set(candidates))


    # candidates = Product.objects.select_related(
    #     'brand', 'category', 'category__parent'
    # ).exclude(id__in=cart_product_ids).order_by('?')[:100]

    candidates = Product.objects.select_related(
        'brand', 'category', 'category__parent'
    ).all().exclude(id__in=cart_product_ids)


    features_list = []
    candidate_objs = []

    # --- 3. Build features for each candidate ---
    for cand in candidates:
        cand_price = float(cand.final_price)
        cand_cat_ai = format_category_for_ai(cand.category)

        # 🟢 اصلاح سوم: استخراج ریشه کاندیدا برای مقایسه دقیق با ریشه سبد خرید
        cand_main_cat = cand_cat_ai.split('.')[0] if cand_cat_ai != 'unknown' else 'unknown'

        p_ratio = cand_price / (cart_mean_price + 1e-5)
        p_diff = abs(cand_price - cart_mean_price)

        is_same_brand = 1 if (cand.brand and cand.brand.name in cart_brands) else 0
        is_same_main_cat = 1 if cand_main_cat in cart_main_cats else 0

        # Calculate dynamic Co-occurrence Score from matrix
        cooc_scores = []
        for cart_cat in cart_cats_ai:
            score = cooc_matrix.get(cart_cat, {}).get(cand_cat_ai, 0.0)
            cooc_scores.append(score)

        final_cooc_score = max(cooc_scores) if cooc_scores else 0.0

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
            'category_cooccurrence_score': round(final_cooc_score, 4)
        })
        candidate_objs.append(cand)

    if not features_list:
        return []

    # --- 4. AI Prediction ---
    df_features = pd.DataFrame(features_list)
    probabilities = recommender_model.predict_proba(df_features)[:, 1]

    # --- 5. Sort and return top candidates ---
    scored_candidates = list(zip(candidate_objs, probabilities))
    scored_candidates.sort(key=lambda x: x[1], reverse=True)
    recommended_products = [item[0] for item in scored_candidates[:top_n]]

    return recommended_products