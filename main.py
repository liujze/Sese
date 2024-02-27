from factory import ConcreteSeseFactory
import yaml
import os

os.environ['KMP_DUPLICATE_LIB_OK']='True'

if(__name__=="__main__"):
    with open("config.yaml",encoding="utf-8") as fp:
        config=yaml.safe_load(fp)
    
    factory=ConcreteSeseFactory(config)
    sese=factory.create_cli()
    resu=sese.run()
    print(resu)