from pathlib import Path
import json
from PIL import Image
import random
import time
from progress.bar import ChargingBar

# Start: Dev only

def prettyPrint(d):
    print(json.dumps(d,indent=4))

# End: Dev only



class NFTM:
    def __init__(self, projectDir, totalArtworks, isAnimated):
        
        self.projectDir = Path(projectDir)
        self.assetsDir = self.projectDir/"Assets"
        self.configDir = self.projectDir/"Config"
        self.outputDir = self.projectDir/"Output"
        self.totalArtworksNeeded = totalArtworks
        self.isAnimated = isAnimated

    def getLayers(self):

        # "position": int(item.name.split("_",maxsplit=1)[0]),
        # "traitType": item.name.split("_",maxsplit=1)[1].replace("_"," ").capitalize(),
        layers = [
            {
                "dir": item.name,
                "weight": 100.0
            }
        for item in self.assetsDir.iterdir()]

        # Sort layers by position
        # layers.sort(key= lambda item: item["position"])

        # print("Sorted layers")
        # prettyPrint(layers)

        return layers

    def getTraits(self,layer):
        layerDir = self.assetsDir/layer["dir"]

        # "label": item.stem.replace("_"," ").capitalize(),
        traits = [
            {
                "file":item.name,
                "weight": 0
            }
        for item in layerDir.iterdir()]

        initialWeight = round(100.0/len(traits),2)

        for trait in traits:
            trait["weight"] = initialWeight
        
        # print("Layer Name: ", layer["traitType"])
        # print("========================")
        # print("Traits: ")
        # prettyPrint(traits)

        return traits

    def generateConfig(self):
        config = {
            "fixedComps":[]
        }

        fixedDraftCompT = []
        layers = self.getLayers()

        for layer in layers:
            traits = self.getTraits(layer)
            layer["traits"] = traits

            draftCompLayer = {
                "dir": layer["dir"],
                "file": layer["traits"][0]["file"]
            }

            fixedDraftCompT.append(draftCompLayer)

        config["fixedComps"].append(fixedDraftCompT)
        config["layers"] = layers

        self.configDir.mkdir(parents=True, exist_ok=True)
        configFile = self.configDir/"config.json"
        configFile.touch(exist_ok=True)

        with configFile.open('w') as cf:
            json.dump(config,cf,indent=4)
        
        print("Config file ready!")

    def getPopWeights(self,layer):
        #returns population and weights in two arrays

        population = []
        weights = []

        for trait in layer["traits"]:
            population.append(trait["file"])
            weights.append(trait["weight"])

        return population,weights

    def getDraftCompString(self,draftComp):
        compString = ""
        for layer in draftComp:
            compString += layer["dir"]+":"+str(layer["file"])+","

        return compString

    def generateComps(self):

        bar = ChargingBar("Generating Comps", max=self.totalArtworksNeeded, suffix = "%(eta_td)s")

        startTime = time.time()
        configFile = self.configDir/"config.json"
        config = None
        with configFile.open() as cf:
            config = json.load(cf)

        # prettyPrint(config)

        # Add empty traits
        for layer in config["layers"]:
            if layer["weight"] < 100.0:
                curWeightSum = 0
                for trait in layer["traits"]:
                    curWeightSum += trait["weight"]

                emptyTraitWeight = ( curWeightSum * (100.0 - layer["weight"]) ) / layer["weight"]

                emptyTrait = {
                    "file": None,
                    "weight": emptyTraitWeight
                }
                layer["traits"].append(emptyTrait)

        visited = set()
        draftComps = []

        total = 0
        if config["fixedComps"]:
            for draftComp in config["fixedComps"]:

                draftComp.sort(key= lambda item: int(item["dir"].split("_",maxsplit=1)[0]))

                visited.add(self.getDraftCompString(draftComp))
                draftComps.append(draftComp)
                # print("Fixed comp added")
                total += 1
                bar.next()

        while total < self.totalArtworksNeeded:

            # Generate image comp based on weights
            draftComp = []
            for layer in config["layers"]:
                population, weights = self.getPopWeights(layer)
                file = random.choices(population=population,weights=weights,k=1)[0]
                draftCompLayer = {
                    "dir": layer["dir"],
                    "file": file
                }
                draftComp.append(draftCompLayer)

            draftComp.sort(key= lambda item: int(item["dir"].split("_",maxsplit=1)[0]))
            
            draftCompString = self.getDraftCompString(draftComp)
            
            
            if draftCompString not in visited:
                visited.add(draftCompString)
                draftComps.append(draftComp)
                total += 1
                bar.next()

        # Calculate trait rarities
        rarities = {}
        
        for layer in config["layers"]:
            rarities[layer["dir"]]={}
            traits = [ i["file"] for i in layer["traits"]]
            for trait in traits:
                rarities[layer["dir"]][trait]=0

        for draftComp in draftComps:
            for layer in draftComp:
                rarities[layer["dir"]][layer["file"]] += 1

        for dir,files in rarities.items():
            for file,count in files.items():
                count = round((float(count)/self.totalArtworksNeeded)*100,2)
                rarities[dir][file] = count


        print()
        prettyPrint(rarities)
        
        print("Writing data to comps.json")
        
        compsDict = {
            "comps": draftComps
        }

        self.outputDir.mkdir(parents=True,exist_ok=True)  
        outFile = self.outputDir/"comps.json"
        outFile.touch(exist_ok=True)
        with outFile.open('w') as f:
            json.dump(compsDict,f,indent=4)

        print("Saved comps.json")

        self.generateMetadata(compsDict,"Test","THEURI")
        print()

        print()
        self.generateImages(compsDict)
        print()

        print("Took ", time.time() - startTime, " seconds")



    def getFileNameByIdx(self,idx,total):
        zFillCount = len(str(total-1))
        return str(idx).zfill(zFillCount)


    def getMetadata(self,idx,fileStem,comp,baseName,baseImageURI):
        metadata = {
            "name": "",
            "description": "",
            "image": "",
            "attributes": []
        }

        metadata["name"] = baseName+str(idx)
        metadata["image"] = baseImageURI + "/" + fileStem + ".png"

        for layer in comp:
            if layer["file"]:
                attribute = {}
                attribute["trait_type"] = layer["dir"].split("_",maxsplit=1)[1].replace("_"," ").capitalize()
                attribute["value"] = Path(layer["file"]).stem.replace("_"," ").title()
                metadata["attributes"].append(attribute)

        return metadata



    def generateMetadata(self,compsDict,baseName,baseImageURI):
        # BaseImageURI ipfs://<hash>

        metadataDir = self.outputDir/"Metadata"
        metadataDir.mkdir(parents=True,exist_ok=True)

        comps = compsDict["comps"]
        total = len(comps)

        bar = ChargingBar("Saving metadata", max=total, suffix = "%(eta_td)s")
        for idx in range(total):
            fileStem = self.getFileNameByIdx(idx,total)
            metadataFile = metadataDir/(fileStem + ".json")
            metadata = self.getMetadata(idx,fileStem,comps[idx],baseName,baseImageURI)

            metadataFile.touch(exist_ok=True)
            with metadataFile.open('w') as f:
                json.dump(metadata,f,indent=4)
            bar.next()

    def getImageFromComp(self,comp):

        img = None
        baseImgNotReady = True
        for layer in comp:
            if layer["file"]:
                if baseImgNotReady:
                    img = Image.open(self.assetsDir/(layer["dir"]+"/"+layer["file"]))
                    baseImgNotReady = False
                else:
                    curImg = Image.open(self.assetsDir/(layer["dir"]+"/"+layer["file"]))
                    img.paste(curImg,(0,0),curImg)
        
        return img

    def generateImages(self,compsDict):

        imagesDir = self.outputDir/"Images"
        imagesDir.mkdir(parents=True,exist_ok=True)

        comps = compsDict["comps"]
        total = len(comps)

        bar = ChargingBar("Saving images", max=total, suffix = "%(eta_td)s")
        for idx in range(total):
            fileStem = self.getFileNameByIdx(idx,total)
            imgFile = imagesDir/(fileStem + ".png")
            img = self.getImageFromComp(comps[idx])
            img.save(imgFile)
            bar.next()


nftm = NFTM("D:\\Projects\\NFT Tools\\NFT Machine\\Project", 10, False)

nftm.generateComps()
