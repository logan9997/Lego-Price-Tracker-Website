

def get_star_wars_fig_ids() -> list[str]:
    path = r"C:\Users\logan\OneDrive\Documents\Programming\Python\WebScraping\BricklinkPriceDataTracker\data\itemIDsList.txt"
    with open(path, "r") as file:
        fig_ids = file.readlines()
    return [f.rstrip("\n") for f in fig_ids]