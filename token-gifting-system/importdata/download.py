import json 
import subprocess


NFT_JSON = './template.json'
IMG_PATH = './images/'
META_PATH = './meta/'

json_f = open(NFT_JSON, 'rb')
nft_json = json.load(json_f)

for nft in nft_json['nft_list']:
    print(nft['data_uris'][1])
    subprocess.call(['wget', nft['data_uris'][1]])
    subprocess.call(['wget', nft['metadata_uris'][2]])

'''
for row in img_csv:
    print (row[0]) 
    subprocess.call(['wget', row[0]])
'''