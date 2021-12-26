from pathlib import Path
import json
from typing import Any, Union
from PIL import Image
import random
import time
import copy
from progress.bar import ChargingBar

import nftmutils

# Start: Dev only

def prettyPrint(d):
    
    print(json.dumps(d,indent=4))

# End: Dev only

class NFTMConfig:
    """
        NFT Project Configuration
    """
    def __init__(self, project_dir:str, total_artworks_needed:int, frame_count:int, seq_duration:float) -> None:

        self.project_dir: Path = Path(project_dir)
        self.assets_dir: Path = self.project_dir/"Assets"
        self.config_dir: Path = self.project_dir/"Config"
        self.output_dir: Path = self.project_dir/"Output"
        self.total_artworks_needed:int = total_artworks_needed
        self.frame_count: int = frame_count
        self.seq_duration: float = seq_duration
        self.fixed_comps: list = []
        self.layers: dict = {}

    # Probably we don't need this
    @classmethod
    def init_from_existing_project(cls, project_dir: str):
        config: dict = nftmutils.read_json_file(Path(project_dir)/"Config/config.json")
        return cls(project_dir, config["total_artworks_needed"], config["frame_count"], config["seq_duration"])

    def get_layer_keys(self) -> list: 
        
        layer_keys: list = [ item.stem for item in self.assets_dir.iterdir() ]
        return layer_keys

    def get_trait_keys_from_layer_key(self,layer_key) -> list:
        
        layer_dir: Path = self.assets_dir/layer_key
        trait_keys: list = [ item.stem for item in layer_dir.iterdir() ]
        return trait_keys

    def generate_config_templates(self) -> None:

        layer_keys: list[str] = self.get_layer_keys()

        fixed_comp_template: dict[str,Any] = {
            "rarity-score": None,
            "extra_attributes": [],
            "layers": []
        }

        for layer_key in layer_keys:

            layer_key_split: list = layer_key.split("_",maxsplit=1)
            layer: dict[str,Any] = {
                "display_name": layer_key_split[1].replace("_"," ").capitalize(),
                "z_index": int(layer_key_split[0]),
                "link":[],
                "traits":{}
            }

            trait_keys: list[str] = self.get_trait_keys_from_layer_key(layer_key)
            
            empty_trait: dict[str,Any] = {
                "display_name": "None",
                "weight": 1,
                "group": None,
                "avoid": {}
            }

            for trait_key in trait_keys:
                trait = empty_trait.copy()
                trait["display_name"] = trait_key.replace("_"," ").capitalize()
                layer["traits"][trait_key] = trait

            empty_trait_key = "none"

            layer["traits"][empty_trait_key] = empty_trait

            self.layers[layer_key] = layer

            fixed_comp_layer_template = {
                "layer_key": layer_key,
                "trait_key": empty_trait_key
            }

            fixed_comp_template["layers"].append(fixed_comp_layer_template)

        config: dict[str,Any] = {
            "total_artworks_needed": self.total_artworks_needed,
            "frame_count": self.frame_count,
            "seq_duration": self.seq_duration,
            "fixed_comps": [],
            "layers": self.layers
        }

        # Write config.json file
        nftmutils.write_to_json_file(self.config_dir/"templates/config.json", config)

        # Write fixed comp template
        nftmutils.write_to_json_file(self.config_dir/"templates/fixed_comp_template.json",fixed_comp_template)



    #################################################
    # Below functions should be moved to a new class    
    #################################################

    def get_comp_string(self, comp:list) -> str:
        
        comp_string: str = ""
        for layer in comp:
            comp_string += layer["layer_key"]+":"+layer["trait_key"]+";"

        return comp_string

    def sort_comp_by_z_index(self, comp: list, config: dict) -> list:
        comp.sort(key= lambda item: int(config["layers"][item["layer_key"]]["z_index"]))
        return comp

    def generate_comps(self):

        bar: ChargingBar = ChargingBar("Generating Comps", max=self.total_artworks_needed, suffix = "%(eta_td)s")
        startTime = time.time()

        config: dict = nftmutils.read_json_file(self.config_dir/"config.json")

        visited: set = set()
        comps: list = []

        total: int = 0

        if config["fixed_comps"]:
            for comp in config["fixed_comps"]:
                comp: list = comp
                self.sort_comp_by_z_index(comp,config)
                visited.add(self.get_comp_string(comp))
                comps.append(comp)
                bar.next()

        while total < self.total_artworks_needed:
            comp = []
            temp_config: dict = copy.deepcopy(config)

            for layer in temp_config["layers"]:
                if layer["avoid"]:
                    for avoid_key in layer["avoid"]:
                        avoid_key: str = avoid_key
                        avoid_key_split: list[str] = avoid_key.split("_",maxsplit=1)
                        avoid_layer_key: str = avoid_key_split[0]
                        avoid_trait_key: str = avoid_key_split[1]

                        if avoid_trait_key == "*":
                            for trait_key, trait in temp_config["layers"][avoid_layer_key]["traits"].items():
                                if trait_key != "none":
                                    trait["weight"] = 0

            # TODO: Create a function to update temp_config

# nftbox = NFTBox("D:\\Projects\\NFT Tools\\NFT Machine\\Project", total_artworks_needed=10, frame_count=1, seq_duration=0)

# nftbox.generate_config_template()