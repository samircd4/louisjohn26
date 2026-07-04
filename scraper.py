import requests
from rich import print
from selectolax.parser import HTMLParser
import json



def get_cos(url):

    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "en-US,en;q=0.9,bn;q=0.8",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "If-None-Match": "\"34ls8z5s2tml7m\"",
        "Referer": "https://www.cos.com/index.html",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
        # "Cookie": "utag_main__sn=1; utag_main_ses_id=1782995543755%3Bexp-session; dep_sid=s_6518665141509745.1782995543758; dep_testdata=normal; hmgroup_consent=datestamp=2026-07-02T12:32:27.245Z&url=https://www.cos.com/index.html&consentId=cca507c9-85e1-4216-85de-ba548bf57104&consentVersion=2.0&groups=C0001:1,C0002:1,C0003:1,C0004:1; OptanonConsent=datestamp=2026-07-02T12:32:27.245Z&url=https://www.cos.com/index.html&consentId=9fd66f01-9f20-4049-a734-a52af5386c87&consentVersion=2.0&groups=C0001%3A1%2CC0002%3A1%2CC0003%3A1%2CC0004%3A1; utag_main__ss=0%3Bexp-session; _cs_ex=1756736863; _cs_c=1; _gcl_au=1.1.82088025.1782995548; _tt_enable_cookie=1; _ttp=01KWHD1Y6G3T0MTBQHYWPQMK3T_.tt.1; _ga=GA1.2.116125589.1782995548; _pin_unauth=dWlkPVlUQTFOV1V5TnpVdFpUbGlZUzAwTnpreExUZzJPV010WVRVeVpEazBNV015WlRNeA; ecom_locale=en_gb; bm_ss=ab8e18ef4e; device_type=desktop; ecom_cart_id=3ebb1aaa76b81d4ca4e1c7eb3701b067; last_visited_category_guest_user=MEN; customer_type=regular; bm_mi=FD8441510DC8AA1B8AB0C06A1C09FBCA~YAAQXydzaHo9CxafAQAAtuHTIgDTag2j9nijtPwx3gEs9t6okCGo36WBlT7YR28lRAZ59VHohtBchwCqnYivJHl8hF7J2kJJzxo8Lm+Dh7emzskCJYSBKS4AFoLrzcwmGpVj5RiXgwXOrob0ZrN6XPgeDpJlqmHr3Dol/VqmH8DEklW7h9xroQbTKtE/ysv/TTyPsVS3Vt12F8ciygIVJysVf9gxbxTb2oxw1VsoAvjWuqEgUbVKZmyY7pyqhjQ8kNeXjXGqJz0pR275YxmAFJrnf4ZcCXhNjfcu76Qj36RNw7IerTq0UECoKua6LhtyjaYmU9I1TSUD5ENoKyPr2y7+pAEQ4BJevoSAoXHUxdWiMz2lqFme8DhYuExdG9t4zjk3Q5GidfHE+XKLXcwQPYc+xKloVz8w7P8hck+WPCOutzaoIIj6oOA=~1; bm_sz=19CAE2BEB78E814425A4E0AAA831C37B~YAAQXydzaH49CxafAQAAtuHTIgCKA14nbTMHyLXzcUJJGBi80MDZH3xBI+KOV8UibkFvGVbnTql8/ssZZx7V++Wu3JFfIau9sWTBf4+tXmXvCmcbJJvNcw+46WjigLZxyNda6X6K5Lv4jiusVVvKp6qjAu+jvs7ZyomDMfr4Yg2UbeXgPRvO4TYXZyKY64QihctCiXTlM9gjoSqjgp5cgOI0mE2fzSQzgoQjumL9aO562JqpYQjX4RlQCF+twuY4Y+ulQ0G6l6mPIGxKuQDFGYkz5kn7EeIQqtjF3z6brVgJ5i02gCle4zlALq8nQ9VWjKchj5D5czob7UvGXpJK3zLWXMk9EX1vupMM2SzcuAfobzwkScNyESQpZ5Mdjf3e5nuon2IAGFvNUKieUWJ7zv0bdmG5QKYYnEB3fXx1Jw==~3748912~3686710; _abck=A1D5FE398098106FD1875D0D03A976D1~-1~YAAQXydzaIA9CxafAQAAp+XTIhA+Dv3YyEpO0PIGfnlbF3YxnpMNtIsXqST0VqzT45W/81wotKe/lUP1fQ1Y1O/Q9tMYTnL/MVR2/iTbj+DdemdeKshc+FOXVtNxED1VnvYKWf/oM6ZRJxWYDToNOb4egS1zG55dvjVXRGvmC4JRVFzW3sw2JSai01eXLe87Ctew5cVGNo9tbUmWwnCU+Gyqzf/dO1Bxw6EYmSk9QImRdrRjeo/PBqrIiS7fTTktYCjll+Wme7Z83opryqVqkj9aNafPaskzjLzhPrHLGU9I0wpcBfE2612Ct7AyMExU06tMx9DLUKMJpSY75GjZwoA1Kmy1SvN23PyGeUU27msXNav1HaoQx3NqO9ARJdZHJBh7HG7mV/AmRZr0ObyXHzFrhJ84NeocPAcUYo9FNr1zl/ku88nNFlj8MO6A3PWUUs3tccFHgDDh8ZX1fu11z91gsMCcgmQOPuOrmGAnK15v6pi5vEi1WqqvUHK51en4/wlej0uWCmCXOIQgi79jt6g2Bfl7tFu6RmH/99yZFUBnmwQazHtt+bPJa4oLtoidF5K1kSMfvVt/WwbS45ufC/Opc0MsRaP/UYL7mReAnR91i11TNMF+G1PAL1wIE2wSPlC1B2EpBQCu44pMBQ==~-1~-1~-1~AAQAAAAF%2f%2f%2f%2f%2f0ILMWhP+QgNFaHZEKo7ghIKL9%2fysrkvnnnB299LAhZsAzRfZwlvliW67gYz9ahyv6DICej22wCdVVh6qSqluJOY6MxAcpwoyqIb~-1; __rtbh.uid=%7B%22eventType%22%3A%22uid%22%2C%22id%22%3A%22unknown%22%2C%22expiryDate%22%3A%222027-07-02T12%3A35%3A51.934Z%22%7D; __rtbh.lid=%7B%22eventType%22%3A%22lid%22%2C%22id%22%3A%223qu2pHPKiT5lRsAXRsxU%22%2C%22expiryDate%22%3A%222027-07-02T12%3A35%3A51.934Z%22%7D; _uetsid=167bee20761211f1bd2bd7914d0dd2e9|w2bzl4|2|g7e|1|2374; ak_bmsc=F4F4FFD97D45C84E8D9EABE599AF0D24~000000000000000000000000000000~YAAQXydzaIg9CxafAQAALCXUIgDr353lHD+gI1za06e0xyNyWUcOgUj45gjZFp295PQOwgV4B1QlH5c+DP8rrE7u/Zw+X5rxxbC+sLo2DKIRDBxFTTINntssyiLp31PRfi17fWRfC/Ixd4/reu1ildv1QysqJvXDaoohLCZIwN8ojPeS3cH3H5uE+naK7xuGjSkzJozTZYsx0zQ6zKuePqUzJ2eGFCMunF/Nmxgz81ha8l0a7On0NSE2owv8FzutdsGN1wZ7Fo3pgcZuNMXPGHIMLfYbv+VZ8SRUBDGDoewumISsrBl/Pw9ad0MW9MWoXqgscz8/6E2VXpiCGeyaeFaqRw3I2lu4F4DsQHRkCIfB47RvLkbv8RLTASPAgS7yql59bOdj/3HGEkXbCUpwPVWBi2m+f3JHumYTLd6UGgbc8XLNGr2P80JIj1GBweSBhfvHitu9f8Y50Q8GAuhS2MTKJZ8Ur3ZDk/Lk+32luZ1PPszYQwFjmTnasyOkz6Sg8eYC08ReNFkvTWYUBUyrRl4kuneLs4Xy1Yd1eEvqXByOus2MoUnZcaEiyCGC9zQgJlYFPOr/fjc=; bm_so=A998AABDDDE51287A01CE7CEF325FBFA37E0BCFF0321055FDB0CBEDBDB7B9130~YAAQLYfYFz9oJRyfAQAA1ZzZIgiEPy/WjNajdX/Ktfy6PEdegvrnaqKfaUnt0xPwDW6bOFYCz+1VlR1DkLOklAPhDmWZ8QgEvwEbpBOXbwquh0GnolGYJFVOpeL0HNU7ORyqrFs7dlvqtBan45CvVhXqLI00Rq+zSMD5bF/Cuc9WD7YpqxobmcAN0mQKPStubo1exgZLXV1Sn/s92LyrQUiKfglMK67GaJGpqItNC5E28YIn1w7btE8md45r51U4Wfn+SgdMHIIcg5Ct1CwwHQ/pyUcCc2KAhUwcONAG7ttobr0PcrggE4BSN9FZQNcnEVkuF4ViLprq+svPiebc07s0v61T+stilkzrKoZw0QYUYo3rVnjhLvN4i4sw1L8mBrdOG3MOUhc9X9m045laCip6h+f/FAhz7H+2G3VwfE/OKh3rrQFc4OW2Bx512gFRwa0Vxg+NqjluTWn6nN6ZGSo=; bm_lso=A998AABDDDE51287A01CE7CEF325FBFA37E0BCFF0321055FDB0CBEDBDB7B9130~YAAQLYfYFz9oJRyfAQAA1ZzZIgiEPy/WjNajdX/Ktfy6PEdegvrnaqKfaUnt0xPwDW6bOFYCz+1VlR1DkLOklAPhDmWZ8QgEvwEbpBOXbwquh0GnolGYJFVOpeL0HNU7ORyqrFs7dlvqtBan45CvVhXqLI00Rq+zSMD5bF/Cuc9WD7YpqxobmcAN0mQKPStubo1exgZLXV1Sn/s92LyrQUiKfglMK67GaJGpqItNC5E28YIn1w7btE8md45r51U4Wfn+SgdMHIIcg5Ct1CwwHQ/pyUcCc2KAhUwcONAG7ttobr0PcrggE4BSN9FZQNcnEVkuF4ViLprq+svPiebc07s0v61T+stilkzrKoZw0QYUYo3rVnjhLvN4i4sw1L8mBrdOG3MOUhc9X9m045laCip6h+f/FAhz7H+2G3VwfE/OKh3rrQFc4OW2Bx512gFRwa0Vxg+NqjluTWn6nN6ZGSo=~1782996110730; ttcsid_CEQ2AL3C77UFTJ8GSBH0=1782995548372::8b52-SUyxaSgOW3761Df.1.1782996124119.1; _ga_N24D02XM9L=GS2.2.s1782995548$o1$g1$t1782996139$j60$l0$h0; utag_main__pn=4%3Bexp-session; utag_main__se=23%3Bexp-session; utag_main__st=1782997940272%3Bexp-session; dep_exp=Thu, 02 Jul 2026 13:12:20 GMT; ttcsid=1782995548372::8VwyVmTQz7T3vaSivoqt.1.1782996124119.0::1.593800.204126::575734.14.1390.461::377347.100.300; RT=\"z=1&dm=cos.com&si=828d60bf-dfc5-4970-9f4d-1eeab9ffbfed&ss=mr3hicvy&sl=6&tt=ery&bcn=%2F%2F684d0d47.akstat.io%2F&hd=cvc7\"; _uetvid=167c0650761211f1af1d755141e3854e|1b2gxx|1782996142830|7|1|bat.bing.com/p/insights/c/a; dtc-token-secure=O8IVjvgEWaXs1FlPSU4vo58UddvOw1YoTyCjZu%2Fxtszqa7JsBVnzGVcmDPYca285weLMmaowp4ATXk4hmdrGBg%3D%3D; bm_s=YAAQIUw5FxT8qPyeAQAAzdndIgWxzlubaJG4QyX1FP4fi84x/Me/TMUTyYraXKgcmhlId1hMonbMyaEH9U1JaiFW1x2gmhe6c4ZLCV7V6+YFCIsbPhoP7ER6gDwTXoEdLBd503zNjozUUU+ITWZoNgtMFnCY6aZzXXXzNVHYBpWKdgOESvb5QrtBMzjuALyXtK7Gzx237mEjfc77Po24N4IiOpMYbiU+F2OSg7obYkBtTlNftbriCqqT1CKfQwQAdeevB7PVZ33MjN05svMNNEWJTryX3h7xVAtvZFWxT2yz320+AyK+AoI4joEIf2jiCdmAv6kL+SiCTChIxt59mJUo7mrpyx8/iU7qPNMF3aWegyN2rVz7Z+YViTZgVLGbfEx47k7mjhTkwcVJ2U2o9ZcuWn0WuSZJTyTvB0DYuJ7VIpW8lviZytXu/DY47I7SKgmOW7zjuQFF7rJfgyt6GHOBJtnkl521eKN/X37VobuqGXvcElr/fd//7Pw8xfaHSfuk3cD/uIJFBTklE88Ela6nAvZXep6c/AchyhmIlT4ACdk2XLS3PKkxsVtVKNDp7uLuEaL3PUrK4cY4u6dMyisDZd0O75Hw/LXi/d//6U0M4p3VYTRYglc9lTx+oQpujSoFudAESqJt5+1kMXNpZAXaYRXiv8JwvBW0r9fVr/zZm8J6+OLfYlPRA1ic2F3+C6DRnRr+TJ8p1C6A0UgZ8BswGFw9Gr7qCTLUECM5BHvq06qHD87W/fMds6xkxbO5jzAcNc1Q8ibBX//3rlzwjqfuSi0xjgdTT/rzNj/1FHTZnyl7YnwagTyZK7KxTgdrOYYbAJbZZNfweLJiVGQ0weWf5nC+jMYslKCxnht7TYANVOIKUrxvVPFVnIHQLNXM6OG/1SzShpI0T1X9O0+L3gSEjhrk/WpFQ79RI6Z4HqXIItmA6VoFgEaEfSkMnwC82DjzA3qdI0yBWGlCSllez3KgndBMpbUzsUQKK6+ClzB7aSiCkwSK26A=; bm_sv=11321EA2673EF6B35883A814A2CC7C6B~YAAQIUw5FxX8qPyeAQAAzdndIgD6Lympdt9QFjTVDVrsvkzKVwKTVIa4vMCZ/vq+9+MrmWneTdZuoDhd3gtfLejCoHT0OsbN6ceaXLNMwwshUwiaAm7u2B8AM8W2pvx/0em+MVfr5Czkiz76Ka7anWpQMApmGGVlgyMcHK/a4cSzSycLcqllQt9h+7fckcgfd+eZnTli98bDT//NxAtZSHMHZewR7vfSofGXhp+4ZvmqEfxeqJHOZC0Opx7UhQ==~1"
    }

    response = requests.get(url, headers=headers)
    html = HTMLParser(response.text)

    data = html.css_first('script[type="application/ld+json"]').text()
    data = json.loads(data)
    product = {}
    product['title'] = data.get('name')
    product['price'] = f"£{data.get('offers', [])[0].get('price')}"
    product['brand'] = data.get('brand', {}).get('name', '')
    product['image_url'] = data.get('image', [])[0]
    product['url'] = url
    
    print(product)
    return product
    

if __name__ == "__main__":
    url = "https://www.cos.com/en-gb/men/menswear/tshirts/regular-fit/product/3-pack-cotton-crew-neck-t-shirts-black-1294699002"
    for i, j in enumerate(range(1, 400)):
        get_cos(url)
        print(f"Scraped {i+1} products")
