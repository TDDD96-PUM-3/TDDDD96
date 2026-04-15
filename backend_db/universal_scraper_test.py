import json
from universal_scraper import get_scraping_data, build_driver

TEST_URLS = [
    "https://www.amazon.com/Bordered-Silicone-Dressing-Waterproof-Breathable/dp/B08BWGVGTP/ref=sr_1_1_sspa?dib=eyJ2IjoiMSJ9.ZV02BNtZXQoBrqQQIy9y-SnmgOmsmvyGQLIc9ZByv9arLpVWq_HFnmLqMaR1Byh-HJRqWCg867DH7PjNGbSR0hmZ2lBLLgGPqGj-QoyF_xTjJmyYb7gcGQ-BebuYS-fgCsreiKdeohhTr6I2SFC0jfgZ1p1rO9ChKjt3QeuIjKIaSBS_NGZ-4hH2S4yOrZwYVpHFrM9mDOQV6bQM6AcjhHQNdpCYA8XhywCPwQhAUZQ.2PRPBRdM7jFg47JBiUcDXpWP7ZSAhGrNSccrwWuXH_s&dib_tag=se&keywords=m%C3%B6lnlycke&qid=1772530320&sr=8-1-spons&sp_csd=d2lkZ2V0TmFtZT1zcF9hdGY&th=1",
    "https://www.temu.com/gaming-headset-p-34567891234.html",
    "https://www.ebay.com/itm/389340071774?epid=12064992096&itmmeta=01KM0K23NBX0V20S7D8CDZBPXQ&hash=item5aa67a075e:g:VQ0AAeSwpKVpNFSE&itmprp=enc%3AAQALAAAA4DKQclQvzFwZQpmMrsO4Luqz69MrBeOo8uj8ZHREq4xNOi0pbtrRJ2Tg7lwpdPOKVgN7KkLGYZktWCh4JK1xPBR6hDDTI26MLFKcatNvP0OMh8HKz8bMsp%2FyMwxSPMLo2e59PMdpdtHvLhfio7HsM%2BvTzLV7MVbObda4Fzcv%2FPdPPZhDyZ%2FmPNv%2Fvdefjm%2Fk5PPOi%2FLTxLRtmOZgVmIHSk%2Bi7SvvCbE8HE%2FbIz4cyLeLJ%2BCR13rQNlhEgNXhW%2B2kKlON%2FjHpMpluNRoV0%2BrVnYqPcq8--Mq%2BxGdqswKRCgrU%7Ctkp%3ABFBM7rqIk6Bn&var=656654952199",
    "https://www.aliexpress.com/item/1005011643932033.html?spm=a2g0o.productlist.main.2.358a5938uzfmeH&algo_pvid=1b7fa8ef-4bd4-42d1-87cd-22c499bfbf5f&algo_exp_id=1b7fa8ef-4bd4-42d1-87cd-22c499bfbf5f-1&guide_trace=353c8c2a-d6bb-4cd7-b142-d5646b6a2f4e&pdp_ext_f=%7B%22order%22%3A%223%22%2C%22spu_best_type%22%3A%22price%22%2C%22eval%22%3A%221%22%2C%22fromPage%22%3A%22search%22%7D&pdp_npi=6%40dis%21SEK%21784.39%21377.91%21%21%21567.25%21273.29%21%402103894417738415382443836eaf8e%2112000056134741775%21sea%21SE%210%21ABX%211%210%21n_tag%3A-29910%3Bd%3A18dd2014%3Bm03_new_user%3A-29895%3BpisId%3A5000000197850273&curPageLogUid=8HHjkrxVlcX0&utparam-url=scene%3Asearch%7Cquery_from%3Acategory_navigate%7Cx_object_id%3A1005011643932033%7C_p_origin_prod%3A",
    "https://www.etsy.com/se-en/listing/1765280597/vintage-fall-sunset-print-autumn?ls=r&ref=rlp-listing-grid-2&external=1&space_id=1314272294773&pro=1&sts=1&dd=1&content_source=3845fe3a9163771f60e9588887d8deee%253ALT17be2aaccb6c48ed7cb372699703c3d3581b62f5&logging_key=3845fe3a9163771f60e9588887d8deee%3ALT17be2aaccb6c48ed7cb372699703c3d3581b62f5",
    "https://www.walmart.com/ip/KONG-Dr-Noys-Plush-Frog-Squeaker-Dog-Toy/19629165?athAsset=eyJhdGhjcGlkIjoiMTk2MjkxNjUiLCJhdGhzdGlkIjoiQ1MwMjAiLCJhdGhhbmNpZCI6Ikl0ZW1DYXJvdXNlbCIsImF0aHJrIjowLjB9&athena=true",
    "https://www.facebook.com/marketplace/item/5511004022338405/",
    "https://www.target.com/p/what-do-you-meme-emotional-support-minis-chocolate-bunnies-stuffed-animal/-/A-94961278#lnk=sametab",
    "https://www.blocket.se/mobility/item/21419403",
    "https://www.elgiganten.se/product/vitvaror/tvatt-tork/tvattmaskin/electrolux-serie-600-tvattmaskin-efi622ex4e105kg/966285",
]


def test_universal_scraper():

    driver = build_driver()
    for url in TEST_URLS:
        data = get_scraping_data(url, driver)

        if data:
            # Print a readable summary
            print(f"\n{'='*60}")
            print(f"{'='*60}")
            print(f"Images    : {len(data['images'])}")
            print(json.dumps(data, indent=2, default=str))
        else:
            print("Scraping failed.")


def test_scrape_url_endpoint():
    from app import create_app
    app = create_app()
    client = app.test_client()

    for url in TEST_URLS:
        response = client.get('/scrape_url', query_string={'url': url})
        print(f"\n{'='*60}")
        print(f"Testing URL: {url}")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.get_json()
            print(f"Images    : {len(data['images'])}")
            print(json.dumps(data, indent=2, default=str))
        else:
            print(f"Error: {response.get_json()}")


if __name__ == "__main__":
    # test_universal_scraper()
    test_scrape_url_endpoint()
