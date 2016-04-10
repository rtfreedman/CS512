import pip
def install(package):
    print("Attempting to pip install {}", package)
    pip.main(['install', package])
