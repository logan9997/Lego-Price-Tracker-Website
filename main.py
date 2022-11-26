from responses import *

def main():
    resp = Respose()
    resp.get_response("items/MINIFIG/sw0001a/price")
    resp.display_response()

if __name__ == "__main__":
    main()

