def log(type=1, text="nothing"):
    colors = ["", "green", "yellow", "red"]
    types = ["", "[INFO] ", "[WARNING] ", "[ERROR] "]
    if 0 <= type <= (len(types) - 1):
        print(types[type]+text)