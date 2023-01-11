from nfttracking.apis import spacescan

testnftid = 'nft1dwkmwkp9q386c9s3rluzdsjut7ry20l4pwremfrfmeejexatvqqske83q3'


def test_get_owner():
    spacescan.set_nft_id(testnftid)

    ret = spacescan.get_raw()[1]
    print(ret['data'][0]['owner_hash'])
    print(spacescan.get_owner())


def test_api_space_scan_all():
    test_get_owner()