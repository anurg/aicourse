def veg(**kwargs):
    for key,value in kwargs.items():
        print("{}:{}".format(key,value))
if __name__=="__main__":
    veg(name="Tomoato",color="Red",weight=5.5)