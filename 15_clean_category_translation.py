import sys

import pandas as pd

#sys.stdout.reconfigure(encoding='utf-8')

translation = pd.read_csv('data/raw/product_category_name_translation.csv')
products = pd.read_csv('data/raw/olist_products_dataset.csv')

print('translation rows before:', len(translation))

missing = sorted(set(products['product_category_name'].dropna()) - set(translation['product_category_name']))
print('categories without translation:', missing)

extra = pd.DataFrame({
    'product_category_name': [
        'pc_gamer',
        'portateis_cozinha_e_preparadores_de_alimentos',
    ],
    'product_category_name_english': [
        'pc_gaming',
        'portable_kitchen_and_food_preparators',
    ],
})
translation = pd.concat([translation, extra], ignore_index=True)

missing_after = sorted(set(products['product_category_name'].dropna()) - set(translation['product_category_name']))
print('categories without translation after fix:', missing_after)
print('translation rows after:', len(translation))
print('\nadded rows:')
print(translation.tail(2).to_string(index=False))

print('\nfinal check: all', products['product_category_name'].nunique(), 'product categories have a translation')

translation.to_csv('data/processed/olist_category_translation_cleaned.csv', index=False)
