ITEMS_PER_PAGE = 1
RECENTLY_VIEWED_ITEMS_NUM = 15
PAGE_NUM_LIMIT = 8


def get_sort_options() -> list[dict[str, str]]:
    SORT_OPTIONS = [
        {"value":"avg_price-desc", "text":"Average Price High to Low"},
        {"value":"avg_price-asc", "text":"Average Price Low to High"},
        {"value":"min_price-desc", "text":"Min Price High to Low"},
        {"value":"min_price-asc", "text":"Min Price Low to High"},
        {"value":"max_price-desc", "text":"Max Price High to Low"},
        {"value":"max_price-asc", "text":"Max Price Low to High"},
        {"value":"total_quantity-desc", "text":"Quantity High to Low"},
        {"value":"total_quantity-asc", "text":"Quantity Low to High"},
    ]
    return SORT_OPTIONS

def get_graph_options() -> list[dict[str, str]]:
    GRAPH_OPTIONS = [
        {"value":"avg_price","text":"Average Price"},
        {"value":"min_price","text":"Minimum Price"},
        {"value":"max_price","text":"Maximum Price"},
        {"value":"total_quantity","text":"Quantity Avialble"},
    ]
    return GRAPH_OPTIONS

def get_search_sort_options() -> list[dict[str,str]]:
    SORT_OPTIONS = [
        {"value":"theme_name-asc", "text":"Theme name Asc"},
        {"value":"theme_name-desc", "text":"Theme name Desc"},
        {"value":"popularity-asc", "text":"popularity Asc"},
        {"value":"popularity-desc", "text":"popularity Desc"},
        {"value":"avg_growth-asc", "text":"Average Growth Asc"},
        {"value":"avg_growth-desc", "text":"Average Growth Desc"},
        {"value":"num_items-asc", "text":"Number of Items Asc"},
        {"value":"num_items-desc", "text":"Number of Items Desc"},
    ]
    return SORT_OPTIONS