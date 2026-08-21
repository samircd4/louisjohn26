import requests
from rich import print
from selectolax.parser import HTMLParser
import json

from playwright.sync_api import sync_playwright

from helper import extract_product_id


def get_cos(url):


    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'priority': 'u=0, i',
        'referer': 'https://www.cos.com/index.html',
        'sec-ch-ua': '"Not=A?Brand";v="99", "Google Chrome";v="151", "Chromium";v="151"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36',
        # 'cookie': 'ecom_locale=en_gb; hmgroup_consent=datestamp=2026-07-08T10:52:46.365Z&url=https://www.cos.com/en-gb&consentId=fd74ff36-ae82-4ee9-866b-35f65158a968&consentVersion=2.0&groups=C0001:1,C0002:1,C0003:1,C0004:1; OptanonConsent=datestamp=2026-07-08T10:52:46.365Z&url=https://www.cos.com/en-gb&consentId=cfce32f6-b077-4851-af97-87e740f2d3cc&consentVersion=2.0&groups=C0001%3A1%2CC0002%3A1%2CC0003%3A1%2CC0004%3A1; _cs_c=1; _tt_enable_cookie=1; _ttp=01KX0NQQESF9YH52XNE0AAD2DZ_.tt.1; _pin_unauth=dWlkPVpqZzFPV1poT1RndFl6UTVNUzAwT1dKakxXSTNObUl0TlRSak16TTRPVEUzTlRFMg; _fbp=fb.1.1783507967596.727483098637404922; _ga=GA1.2.1876326202.1783507968; last_visited_category_guest_user=MEN; bm_so=AD8EFD1ED4E3DC80A5A0EB2F66F033E1073531E043577523FADC4F75268FA49A~YAAQLYfYF0IeeR2gAQAA673nJQgzrfJ9VmtUf0YtqEKzyydvsVYTp1EeIf282auEOp/iXQQ/mt8D16oAFi+SljrPlW6GCyj0XpbYzox0LHGAwOTE3884CcNKwTA1AavNT5cVEMpSQyQ57ALqsWKKskBJ/FuqfiN23RX2QHAon4TnMgTLhBgQ9m0kWqFWTgVOx/2/SNfB2XF6EDPWCqm8p2cWuayYfVOUk+YaEDt20LLmI7hhBY6FJ78GfMep2jSSOsncZZmAeJcBk8ECcuZ3lnX1zAwC23rWm2GsaO9CWHhWBkz1ydec453cwnDuat0n8QmdKUwGkz72H8hVKZwrPgLfqjKjK0jcRJkCDrY7SeeOabnj71HPV7L4XBzs1012wi6JtxCJsp3sDMik8i8FEXSGrwfk0mmRc9cgCLUVi9j/FevIpi+W6rB/kPg0uFaNpos+WcSmdCeiKRBKLo72I0M=; bm_mi=77E6EB619781A56C0D3187C7381E6489~YAAQLYfYF0weeR2gAQAAfr7nJQDRzn3r/88IrVEHtnWS+vstyR+LQJvWl7DfmOW3yBEEeSgB43nT8QmZSc2tsbHhNtFG/RL++O4dYN/Lx11S5sy91AO9hVvZFIwphmbdtQqyxNSoK/IenwzwAUH4fDboJiJtZKQl/5COlkZds7UgYIRdSoXSFZ/wAcpvDpA/qGcVA0kk1rz/auaXtI2CjZ3r45g3szoto03dmihoVfDsoYDOW30M45I7ZCdM4vwIj5oFsSJ9oECa0MDFM8vzXeknP8simFNjgecYaeS7VCyGIO1cV4ky6BAT1MyQmbgyHcNXSA==~1; utag_main__sn=3; utag_main_ses_id=1787342339399%3Bexp-session; dep_sid=s_5949751721922851.1787342339401; dep_testdata=normal; bm_lso=AD8EFD1ED4E3DC80A5A0EB2F66F033E1073531E043577523FADC4F75268FA49A~YAAQLYfYF0IeeR2gAQAA673nJQgzrfJ9VmtUf0YtqEKzyydvsVYTp1EeIf282auEOp/iXQQ/mt8D16oAFi+SljrPlW6GCyj0XpbYzox0LHGAwOTE3884CcNKwTA1AavNT5cVEMpSQyQ57ALqsWKKskBJ/FuqfiN23RX2QHAon4TnMgTLhBgQ9m0kWqFWTgVOx/2/SNfB2XF6EDPWCqm8p2cWuayYfVOUk+YaEDt20LLmI7hhBY6FJ78GfMep2jSSOsncZZmAeJcBk8ECcuZ3lnX1zAwC23rWm2GsaO9CWHhWBkz1ydec453cwnDuat0n8QmdKUwGkz72H8hVKZwrPgLfqjKjK0jcRJkCDrY7SeeOabnj71HPV7L4XBzs1012wi6JtxCJsp3sDMik8i8FEXSGrwfk0mmRc9cgCLUVi9j/FevIpi+W6rB/kPg0uFaNpos+WcSmdCeiKRBKLo72I0M=~1787342339519; scarab.visitor=%223D2CE2ED2795FF1D%22; _cs_ex=1756736863; ak_bmsc=1CBF4E4AC74F98D3AE33644CA1013F06~000000000000000000000000000000~YAAQLYfYF54eeR2gAQAA7cbnJQBsCAuqkuSIB9UwdfIGogXmKPm5boIuDH3vRX1yIHEvNVtKmQnLjoXKbXdJ6DDG08Zq+doya00YEM6lQCVVZXALTrH0MarBsODeWEPp0nEaPfNE+11K5oDO/rEWizzopZla5+RVX+SVc1HiNMB+xKKBAOdNn0hs/nG5mKU58nZPrqcfV52zP+C/lXN+xSNdFkvfnG1I+cwPEAsolqMMNmfQQjmVXjQ00rLNunslwQzMKYmFiyk8CHkc07cbSYkPBmtkE5Y8xJdKPLSpAzprsm7r5RcMY18sS9IGfzo1jGhzHDnOUBVovfeMbxavBbS7W1dHm33b097czSvTQH3nZ9MrkqIMhisK9KFoJwsFJeQrxWNEsIrCuyPFPH2LB2t2EqlhJByugX0cCaMT33ZIrN8rGiDPk4lEDj29raQnH3Ab/41bIMFsEVAepTm7FjKPim1C+A5tVXtJRIyOeAGdgs0fvxuJjmE=; utag_main__ss=0%3Bexp-session; bm_sz=7DF99735445CDEE02198F0F840C6BC84~YAAQLYfYFy8feR2gAQAAjtbnJQB8xnS/hbf3rOuhJGsa7TV0Ny6jsVJhbifrPZJyqLtZMV8KvK5yoW29LZW1XvQ+JM7lzyciEjUOUQEVxg+SiYqlgTcENkF0GiDkVectTvhM3SeG7NEinVsJWnl7qCxmQaVp4NTAz1/DvSWfXA451KEepAFBfQzcE9cH7FahXYIAJwnRpuI3Nig1yeZiiWedJLfTo/G0TMzP2mThECBX12HdQkAarRKTvO24McqH1fuZ98rQpdzyZqZDarTkKXy/1RoovZSrVezFfHVsw/5tORlfDlWwxjqYVUM/6uqUA6Xj5tUptDKc+XEsJ6GY9KE3f0S1kZj+xc6iH1FTvG5ZPujSPoUPvxX+6XDWpsLEtZPXFXZLwO7EBGWabzgoacpwCvBirg==~3355952~3158593; _abck=593E57E75133B6C806D302ED3B3B2E86~0~YAAQLYfYF1AfeR2gAQAAOdrnJRB8dwmSwSFzg19H39ok3f8frCzR3gcAlmJrJlzyz4nww4AJzkF33ppGDB3QYHS/KgtzOGpUjjDpHY7BFpAcD42vTZptbgSpNBZfllUD2MUPc3riZZm9c7A7cyIbQhAS8KMVnGjidZCL1w+DYE9u7SCjlTQWU+XAgL/LcibopEQIcMnX9dXiYjtnU64rQU/W37D1L12OmOT2dfaK3EqDQEDhC8etdODZC1+yt1TOwoCSmubwzXM2KfzQuYDC+VCnjf6RHUxpNII2S9qGntitWlwAm6ZAEzK1iUmsR2CKdD+QJFAwiTmaURi7H6n3xaGqaVOacYFx3zLL35/kKH79Ef16CWDtK+tVQs6CC3IU3wio9Gyg2/P+e8d2EiHjX5opi2EgdPj5incZ8zUH2Tw3fmOFmrhNIQpes+wiItPg6P/mmVO1ijVKYgMaOEmBllbfUBz0Ok/JhwFe1/Y9iv6s+78aqxxfTtblqbk7r2JCXpfAZirbpPz9fRqzKO04T06XUbzHSp8LoDRNkIFlCfiqRCE1M3uwTXEPpruJRFfwM3K4puqSzlq390lsK67MU0brO8qZusqnFrganKN8bu+//1Y62T3Bx4qHN1Fgk16EhDiBYQerWSldweaz1X0=~-1~-1~-1~AAQAAAAG%2f%2f%2f%2f%2f+MOq+wqYpm58NiEQT41iSyuSC2wdjcGGFWCC21Begm0iTXYp%2f9iqssMySA4+46JXlFb1S6IOOMdhtkqKT3jRHlD90U5QqH+trpG~-1; utag_main__pn=2%3Bexp-session; device_type=desktop; _gcl_au=1.1.2022222357.1783507968; __rtbh.uid=%7B%22eventType%22%3A%22uid%22%2C%22id%22%3A%22unknown%22%2C%22expiryDate%22%3A%222027-08-21T19%3A59%3A06.491Z%22%7D; __rtbh.lid=%7B%22eventType%22%3A%22lid%22%2C%22id%22%3A%22wmTOOPYez5nqAyJKkJKp%22%2C%22expiryDate%22%3A%222027-08-21T19%3A59%3A06.491Z%22%7D; ecom_cart_id=f5b9ec89f09c1da4c7e652ae740ee7ae; customer_type=regular; _uetsid=c02420509d9a11f1abc819cfb1791833|9j4opm|2|g8s|1|2424; dep_exp=Fri, 21 Aug 2026 20:29:12 GMT; scarab.profile=%22g%252F1347336001%7C1787342354%22; utag_main__se=12%3Bexp-session; utag_main__st=1787344152531%3Bexp-session; _uetvid=280f34b07abb11f1bdee3d7d396ea93d|aw4lbw|1787342352603|4|1|bat.bing.com/p/insights/c/l; _ga_N24D02XM9L=GS2.2.s1787342340$o3$g1$t1787342352$j48$l0$h0; RT="z=1&dm=cos.com&si=226cb62e-35ef-46fc-b823-f2e0c27c7894&ss=mt3dha8k&sl=4&tt=863&bcn=%2F%2F684d0d46.akstat.io%2F&nu=mnjuuupz&cl=9r4&ld=c2u"; dtc-token-secure=i1EmncfCIKzVxoLZiq34jAhNgaY4rijdNpiqZjotqvmKwPJ7pj9ApRywoF81EjBoQu5rWEa8hWCu%2FrxWeJU9JQ%3D%3D; bm_s=YAAQJ4fYF+kbnvOfAQAAQMLpJQVg0TWUbSO74Z1i6/m9pP1rANc5S6TkBRE8cPSdxNIL4kioknNnKP/PhVcpd2t+UasWaaPFMfGGPcyhjZLRlpoCuL4usp4DEFPgTEoUtxmU7NEKhex7v4Vye9ij+4pgVzW6reFHr9PePrONsT+L5arvaztmDv+rC/KEDcPTUQyfl1QApMVE6p0WFUrcdnbO0eS2Tefr988mI8q7+PEw1CCqeQDBZT21svTMYhBd6ZXvJI7ik5NpjqFTZ5HKHSyW2XwXoG5ktC/ZxfRDhUs6F01sdTPQDAiDWIJDnUPcdZ7+NgJY0HviaAw9yjiPQg+1lozX/pwEmssiZBtdA77s8Zw+CI7qfBsrIXSjuDGHYK60IqwU9DvZaSEvIxB6fzh4lft568SE69mzhiNyrJgQS3TCGBJbNqP1hmfJp8aC4s+4wp+h1ituJKFYNTtxz5u/81o/ZiRGm1b8SbgHrR7SHmDMWXJyWBdNdU4OZpvrDNbZemaXaX5jSqatbvFuODxePN7cVAhWCQvG4qzcX12cnWqPnHLD3y2ryVzkYbtK+C4t6NEAbQDevWg2iDoA7HdoXwPTuFhsMX4apJDf8UJeCKw+ck3t8eVGvFya7HBBEkYEPR8CKvDcRDTo1ERqq6Bk6pu65PAyeV26Y17gq0zHQhbfc5WRY+6ogOui10o2nNk2a0/ZFI8r4Q50Awq5k+6ysdH2QoxHC8Aau6+1OVH0DZT0xDZpu5yHGGEvJMGfIHJiGEYhW82ueDxsL1LcpgFzCcGaM836XqmeQcbVRhFM/2o0bAk/FP7lxkHcteSlyW1lXoL6tu9QKOJY3HbMWorIKxp6zyd4wVtEvqXZyfklhWvaXm4F0WNlBVIobE8OdkOHHg1buqdXiapnMiMlZVlqP+t8GfibhjRyc3vl4DzRbAtDMqVTSNdZxT5U+yWE7bzHFwIrJND2iqblXlsm/vf/ZUEMM8QotQnEvZLd8R46x1b605D2a/WsXfxBuqCQiLsYKJpWfuqMw9TDuqU487BV/HmUtGtGFx2xCNJKFIXdd4a1lbwy68bpiPIHtA==; ttcsid=1787342340049::wCet34F2s2O0FdwgM6Qm.3.1787342470863.0::1.11815.6255::130812.5.421.390::12221.22.0; ttcsid_CEQ2AL3C77UFTJ8GSBH0=1787342340048::hHcvqtzp_d8q3zsYPHL3.3.1787342470863.1; bm_sv=74D0F2616E1890D813AE2A73EF03B2AF~YAAQJ4fYF60cnvOfAQAAzdPpJQATklTvTOEray9FqUjJjq5G1/4SOkt3UO/xlveS7B7bGE22YAo+idzCgo25qYkzadAkN6lFjeeDLtf7LYNlcbWloODniLsRakH3dt39KSgiVZF+phG9O/p8yGDUrlKa0FXSAKv1CLqCxWyVgMIcEzEhQIYo64Vh8FpP5YsXmF5g7gcwJD1JPuihjKJ7F5wksLnlwhrGgEg1xDl+H1TdfBEDFzcRECe4tpAlgA==~1',
    }

    response = requests.get(url, headers=headers)
    html = HTMLParser(response.text)
    print(html.html)

    data = html.css_first('script[type="application/ld+json"]').text()
    data = json.loads(data)
    product = {}
    product['id'] = extract_product_id(url)
    product['content_type'] = "product"
    product['source'] = "COS"
    product['title'] = data.get('name')
    product['price'] = f"£{data.get('offers', [])[0].get('price')}"
    product['brand'] = data.get('brand', {}).get('name', '')
    product['image_url'] = data.get('image', [])[0]
    product['url'] = url

    print(product)
    return product


def get_cos_with_playwright(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        page.goto(url)
        html = page.content()
        print(html)
        page.wait_for_timeout(5000)  # Wait for 5 seconds to allow any dynamic content to load
        browser.close()


if __name__ == "__main__":
    url = "https://www.cos.com/en-gb/men/menswear/tshirts/regular-fit/product/3-pack-cotton-crew-neck-t-shirts-black-1294699002"
    for i, j in enumerate(range(1, 400)):
        get_cos(url)
        print(f"Scraped {i+1} products")
