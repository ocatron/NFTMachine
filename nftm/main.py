
from nftmconfig import NFTMConfig


project_dir: str = "D:\\Projects\\NFT Tools\\NFT Machine\\Project"
nftmconfig = NFTMConfig(project_dir,10000,1,0)
nftmconfig.generate_config_templates()