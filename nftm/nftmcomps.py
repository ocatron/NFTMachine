from pathlib import Path
import json
from typing import Any, Optional, Union
from typing_extensions import Self
from PIL import Image
import random
import time
import copy
from progress.bar import ChargingBar
import nftmutils

class NFTMComps:
    def __init__(self, project_dir: str) -> None:
        self.project_dir: Path = Path(project_dir)
        self.assets_dir: Path = self.project_dir/"Assets"
        self.config_dir: Path = self.project_dir/"Config"
        self.output_dir: Path = self.project_dir/"Output"
        self.comps: list[dict] = []
        self.visited: set = set()

    """
    Comps structure
    comps: [
        {
            rarity-score: 1212214
            extra_attributes:[
                {
                    "trait_type": "Base",
                    "value": "Big"
                }
            ]
            layers: [
                {
                    layer_key: 1_layer
                    trait_key: trait_1
                },
                {
                    layer_key: 2_layer
                    trait_key: trait_4
                }
            ]
        }
    ]
    """

    def get_comp_string(self, comp: dict) -> str:
        comp_string: str = ""
        for layer in comp["layers"]:
            comp_string += layer["layer_key"]+":"+layer["trait_key"]+";"

        return comp_string

    def sort_comp_by_z_index(self, comp: dict, config: dict) -> dict:
        comp["layers"].sort(key= lambda item: int(config["layers"][item["layer_key"]]["z_index"]))
        return comp

    def get_population_and_weights(self, layer_config: dict) -> tuple:
        #returns population and weights in two arrays

        population = []
        weights = []

        for trait_key, trait_config in layer_config["traits"].items():
            population.append(trait_key)
            weights.append(trait_config["weight"])

        return population,weights

    def update_grouping_config(self, group: Optional[str], layer_config: dict):
        if group != None:
            if layer_config["traits"][0]["group"]:
                for trait in layer_config["traits"]:
                    if trait["group"] != group:
                        trait["weight"] = 0

    def update_avoid_config(self, avoid: dict[str,list], layer_config: dict, layer_key: str):
        if layer_key in avoid:
            for trait_key, trait in layer_config["traits"].items():
                if trait_key in avoid[layer_key]:
                    trait["weight"] = 0

    def generate_comps(self, config_file: str) -> Self:
        config: dict = nftmutils.read_json_file(self.config_dir/config_file)
        bar: ChargingBar = ChargingBar("Generating Comps", max=config["total_artworks_needed"], suffix = "%(eta_td)s")
        startTime = time.time()
        
        total: int = 0

        if config["fixed_comps"]:
            for comp in config["fixed_comps"]:
                comp: dict[str,Any] = comp
                self.sort_comp_by_z_index(comp,config)
                self.visited.add(self.get_comp_string(comp))
                self.comps.append(comp)
                total += 1
                bar.next()

        while total < config["total_artworks_needed"]:
            comp: dict[str,Any] = {
                "rarity-score": None,
                "extra_attributes": [],
                "layers": []
            }

            temp_config: dict = copy.deepcopy(config)
            
            group: Optional[str] = None
            avoid: dict[str,list] = {}

            for layer_key in temp_config["layers"].keys():
                comp["layers"].append({
                    "layer_key": layer_key,
                    "trait_key": None
                })

            self.sort_comp_by_z_index(comp,config)

            for layer in comp["layers"]:
                layer: dict = layer
                if not layer["trait_key"]:
                    layer_config: dict = temp_config["layers"][layer["layer_key"]]
                    
                    # Update temp config
                    self.update_grouping_config(group,layer_config)
                    self.update_avoid_config(avoid,layer_config, layer["layer_key"])

                    population, weights= self.get_population_and_weights(layer_config)
                    selected_trait_key = random.choices(population=population,weights=weights,k=1)[0]
                    layer["trait_key"] = selected_trait_key

                    # Set linked layer traits
                    if layer_config["link"]:
                        for linked_layer_key in layer_config["link"]:
                            for layer in comp["layers"]:
                                if layer["layer_key"] == linked_layer_key:
                                    layer["trait_key"] = selected_trait_key

                    # Set group if specified
                    temp_group: Optional[str] = layer_config["traits"][selected_trait_key]["group"]
                    if temp_group:
                        group = temp_group

                    # Set avoided traits
                    temp_avoid: dict = layer_config["traits"][selected_trait_key]["avoid"]
                    if temp_avoid:
                        for avoid_layer_key, avoid_trait_keys in temp_avoid:
                            if avoid_layer_key not in avoid:
                                avoid[avoid_layer_key] = avoid_trait_keys
                            else:
                                for avoid_trait_key in avoid_trait_keys:
                                    if avoid_trait_key not in avoid[avoid_layer_key]:
                                        avoid[avoid_layer_key].append(avoid_trait_key)

            self.sort_comp_by_z_index(comp, config)
            comp_string: str = self.get_comp_string(comp)
            if comp_string not in self.visited:
                self.visited.add(comp_string)
                self.comps.append(comp)
                total += 1
                bar.next()
                    
        return self