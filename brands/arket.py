# Built in modules
import sys
import os
import json
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Installed modules
from selectolax.parser import HTMLParser
from rich import print
from curl_cffi import requests, CurlError
from dotenv import load_dotenv

# Custom modules
from helper import BASE_URL, STATIC_ROUTE, create_thumbnail, _attempt_download, get_bm_s_cookie


load_dotenv()
PROXY = None # os.getenv('PROXY')
MAX_RETRIES = 5
PROXY_SPIN_TIMEOUT = 5  # seconds


def get_arket_product(url: str) -> dict:
    """Fetch and normalize an Arket product record from its product URL.

    This function requests the product page, extracts the product JSON-LD data,
    downloads the main product image into the local images directory, creates a
    thumbnail, and returns a normalized dictionary containing the product ID,
    title, brand, image URLs, and source URL.

    Args:
        url (str): The public Arket product URL to scrape.

    Returns:
        dict: A normalized product payload with image and thumbnail URLs, or an
        error dictionary if the request or parsing fails.
    """
    if not url or not url.startswith("http"):
        print("[red]Error: Invalid product URL.[/red]")
        return {
            "error": "Invalid product URL",
            "source": "Arket",
            "url": url,
        }

    try:
        time.sleep(1)  # Sleep for 1 second to avoid overwhelming the server
        with open("bm_s_cookie.txt", "r") as f:
            ARKET_BM_S = f.read().strip()
        
        cookies = {
            "bm_s": ARKET_BM_S,
        }

        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "en-US,en;q=0.9,bn;q=0.8",
            "cache-control": "max-age=0",
            "priority": "u=0, i",
            "referer": "https://www.arket.com",
            "sec-ch-ua": '"Not=A?Brand";v="99", "Google Chrome";v="151", "Chromium";v="151"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36",
            # 'cookie': 'dtc-token=59c43bf8-ba0d-4b59-b601-9af70ecfc8b8; bm_so=579332F755A0117BF04F93E07027870B5A63FB7AE507E5767F3F4BCED04DD4B8~YAAQKUw5FzmRPxygAQAAFyBnTAhATGnXYiDAkIPvMLuNWu9vxDsrQyA1PZk8Lq55udtNe3NLkesTYNab9+A8YptliVOCoj81uUy6m1Wc0wMTZLdUtZNvLFjXEayyBA3W76993D9K3ZsncrJfzdn/lm3LDi2IcvOHY5YflgkyALNw3ab5BRbygHkZdPcfqCec2WihAaDBQz7huGaOozoPLwKtdjexPFrgl3Y2aPzQoHof9PIAw5GZAZaJ4a0eUw35yKFTpWFev0Ss+ydDFte/Kjr7Z5aKNb9EXZO1hvwy5DfFD4EvW4UICjhC7oQtKsWYHvrkJ9tmVtJTYN9M6Tz8QxvKIgypU9NZ5lOKw4CYXmTUQcBqB2CjWmwHxBIx526lyzPB4FN1grEy96ZPLLBRbmSG5+opeR2XFM//ciI/5BlUt8KrT+aCio8dQYdqCd6ktkcdCeyYeAuc2i0OMLVfDejTNA==; utag_main__sn=1; utag_main_ses_id=1787988218346%3Bexp-session; dep_sid=s_0105363787918185.1787988218349; dep_testdata=normal; utag_main__ss=0%3Bexp-session; hmgroup_consent=datestamp=2026-08-29T07:23:38.994Z&url=https://www.arket.com/en-ww/?srsltid=AfmBOooQtXO0-Z5cQdjh0lW74HlgmGHf2iSo7HB9mW_XGy-QXck2JZc8&consentId=0006195c-169b-4ab6-a931-f64d21f8b3ca&consentVersion=2.0&groups=C0001:1,C0002:1,C0003:1,C0004:1; OptanonConsent=datestamp=2026-08-29T07:23:38.994Z&url=https://www.arket.com/en-ww/?srsltid=AfmBOooQtXO0-Z5cQdjh0lW74HlgmGHf2iSo7HB9mW_XGy-QXck2JZc8&consentId=0627aa6a-264b-4613-a57c-cca002f09f9a&consentVersion=2.0&groups=C0001%3A1%2CC0002%3A1%2CC0003%3A1%2CC0004%3A1; _cs_ex=1756736846; _cs_c=1; _ga=GA1.2.1254815837.1787988220; _tt_enable_cookie=1; _ttp=01M166E6AX6XHHS3Y630GMBMET_.tt.1; ecom_country_confirmed=GB; ecom_country=GB; ecom_country_confirmed=GB; ecom_locale=en_GB; HMCORP_locale=en_GB; HMCORP_currency=GBP; AKA_A2=A; bm_mi=B84B6F7936C867BFA91B50165C322342~YAAQKUw5FxeTPxygAQAAllVnTADCG0ES8m0Joshv23Fif8O+tV0ZrPurB97xQnJzvIJl8HhKjieDwlkcfJ7DpheHp/bnxgFmcaJOYDVa+jtBUjrfZYiRs4c62l4VCXTmsloSG9pICC/MY7z2wfelKxyjuNUbp8qaOMRemhgvcypdlaqWQb2QK+pFApm5f8M3jutinqWFwmhnO8TX7dYdinStFQyfyqKV5nynbBPtvTMRNCZ+JHSxs0QjDVfuSFAJKqXrT0xZXreh6YKCd5K5SdwYvbKZNBMSF/sRBkVhOSD9E4QuN5kKt9Y5dsHaNP7+YeQl~1; bm_sz=A687F11B53FD0593753CA7F2D4F5975C~YAAQKUw5FxqTPxygAQAAllVnTACX5/2IOCw9guqelUUJd1QET4RO/767159W2/6eAFPUS6y95+DW7pbvVjO4mjweUpPaUjyjH14aqGn5t5d/Z3u2o8BCRHYxc3lo5V5+rf1AcE8BcBRUEDSEvINF0542NqL3OGpE+9S33h1SdzRU1b8NP9kWbXhUkcY3KODXpNuyE04SwJI9i99EPtVHztcC85uIXnKy+qE0Ql3qWoaObjFcV8MrkdH3+9QKyJPhXwVgbX276jXvM+oloyC1lkKNnRZ4DbzfD95+epdGK7XoM84l1HQqhG+aC+Hbn5mTeEgfwr93C3kOCa1UaZmo1rokdy47gkEG/aZlZW4K5jMtXC2Gaib8Y6KCZga+h3XgmVkjM5rw59jwBZIGJtfCCuhTyP0k7wKzlA==~3621175~3356738; _abck=1268616B912DE3ABEA0CAE973F925A29~0~YAAQKUw5FyKTPxygAQAAHVZnTBD4aoUK1rYyLqnhGkqglmm9SCzDpm9j3RlqYk0IYUbC+N+RSdhd871r4DDGdmuxaygLOROEAS3CECv2HDDDlhqO6iMRu6Dasa434WFZdRatpY7PomL2mBUAz5zNPoHUeFrtfO6RQNz79a8QfTEP/YBpkRrygV9FDkR5CZuIaxJvX1b5PCYstUs1ZFKXpv87otQV0iBY6EjaN4T0khZO/Okm5PaaHeOYuz8YwhTRh1cqnCI2HS+L+oaUteDIa94Xn9KAKcT+5Tvt3PcjUExCy2owbt1rtS6m24PzgicDdllsHKqjFFAAIIE7qfrB3FXK6XjmRL2CUqZcEvZhaZ2mWWItfY4wdTMGGm6ZoFjBYZ8Cg3sO3ZbTENiwmbEZUudqRzQrCgXsyy0M3x+wObrrkN5+fpMRU4NxEPOI2NwZ3a7YUfaa/Q668nknt1p7bfbw2JbvjyjEixTJeB4HWmF6L0EIWf/g4WQXbvj0ohO9gbFK/YdH0gA93ZqATKvejXObRIURfPYJOnOgp+N6ohcPDV1wrv+2IKseAm3C7SXdHg1W0CS2ftXsKNi2Jt+1InQ+paXj+W1sllJRxuRQBWyIQ6PhB0IdLUmKQEP2uv0VArOzUY+jrY0=~-1~-1~-1~AAQAAAAG%2f%2f%2f%2f%2f1yWTQey5u5uCMLLiI5cRQQcQadqP1YG3edZJNbrkVB%2fZM5CM5JC2qGlW5fWUpMMUTuVNvu49a7dQu4KttxRj%2f6GDNkXdZN9Vt7z~-1; attraqtsessionid=d5b01a24-13cc-41c2-adae-c497a313f482; merch_cid=d0e93424-4896-4d6a-9c24-fa03ab954dfc; merch_sid=37f9aa43-0520-4b50-b5ca-836df380396d; bm_lso=579332F755A0117BF04F93E07027870B5A63FB7AE507E5767F3F4BCED04DD4B8~YAAQKUw5FzmRPxygAQAAFyBnTAhATGnXYiDAkIPvMLuNWu9vxDsrQyA1PZk8Lq55udtNe3NLkesTYNab9+A8YptliVOCoj81uUy6m1Wc0wMTZLdUtZNvLFjXEayyBA3W76993D9K3ZsncrJfzdn/lm3LDi2IcvOHY5YflgkyALNw3ab5BRbygHkZdPcfqCec2WihAaDBQz7huGaOozoPLwKtdjexPFrgl3Y2aPzQoHof9PIAw5GZAZaJ4a0eUw35yKFTpWFev0Ss+ydDFte/Kjr7Z5aKNb9EXZO1hvwy5DfFD4EvW4UICjhC7oQtKsWYHvrkJ9tmVtJTYN9M6Tz8QxvKIgypU9NZ5lOKw4CYXmTUQcBqB2CjWmwHxBIx526lyzPB4FN1grEy96ZPLLBRbmSG5+opeR2XFM//ciI/5BlUt8KrT+aCio8dQYdqCd6ktkcdCeyYeAuc2i0OMLVfDejTNA==~1787988232129; utag_main__pn=2%3Bexp-session; ak_bmsc=ABD190EFEAAE91CCF225713ACA9DCBE8~000000000000000000000000000000~YAAQKUw5FzmTPxygAQAAo1lnTACxa3ITbwyw+m9f0rqWmxH2lans9s4iMaPbHFXt0RD0a1JAQrWEPbWjxUZdozL8N4PeNzRty3OzLrUd54TscplcSMhjQYuLMPbdiX7j9c+25zLQYBV+umBC/Ja64v1/F5GAKcCS4lzdvl96iicz2jyUCMLgTlPy76nAU9QgEkk61kidohJoTSMt85TfHLtWet3kSKaksCgT/zemxMC/tTlG+7U9oz1KpAQrTxdqY6CEF0rLl0h5Fy9WUx/GLV0qs94moSR9y5FQa4v8D7oq/FBA7CKo2VDhLCsCy1EyET1v0K3Defgmn6ykAnxxZx4OlgU6XxwdX+JMayMu2kBigQFHrRgj873gnYZOqDWSnc//0Y4HttEXOd301AlJCTii3XJLwvOJwq0EI/trC63LFQOhshiXD6uYLnvJlBY4kR7F+mQ9UV3wyuHcHiWn3jWLVAKvB91SnQEiyXeX3mBcK35hjVjAOw==; ecom_cart_id=d4f62c212c25c92f853f3d19134e9718; _pin_unauth=dWlkPVltVmxOR1UyT1dFdFl6TmtPUzAwT0RsbUxUaGlabVF0TkRZNVkySTFZMlJpT0RFMQ; _uetsid=8eb3f8e0a37a11f1ad5bb1a7984551b9; _uetvid=8eb43100a37a11f1acb8174f19be7ce9; _ga_KBVJ8Z4ENB=GS2.2.s1787988220$o1$g1$t1787988257$j23$l0$h0; _gcl_au=1.1.1762227353.1787988220.-.-.1787988241.362883086.1787988242.1787988257; ttcsid_CEI60H3C77UFTJ8GJ2PG=1787988220254::MuoR0WUvAzufCmyTE3c2.1.1787988257815.1; ttcsid=1787988220255::CzJlBncO7ZsZpPCypO6J.1.1787988257815.0::1.37397.13031::37386.8.993.1780::37487.33.0; utag_main__se=21%3Bexp-session; utag_main__st=1787990058358%3Bexp-session; dep_exp=Sat, 29 Aug 2026 07:54:18 GMT; bm_s=YAAQKUw5F1mzPxygAQAArbFqTAbackBDk4V8cmy9CsMx/914EY503o5dTQ4GZ/QiauyJ6XjOwSJqqi5QddXq8Z3kQepsvQwDI0QvnbqN9Yr6zH6+82w+2asfCx6cp93Xp3n0VuKBNG3RIFSDBuCjHz9o8K5fbcizUMcqZxWg1KRytnkKwvt/FpLtZ2TpQU8aOLZZZtkAA0UJf6y8vkNNBkZeQOkawu0TRcn12Ksh2P5xcoIvoBTyjmgpXW7L5oKJdB5UcISD2WMZtVYn1UorLfKZh2mOfQEh+KHepxxU5RpNjZb4q5S4sV7HrBUVppWFD2X1kSgxnD0uBcEpo/M38+itTMcS9DTvraK7+32smKBIML2um41zJELPT56nl+6h6yP1vXol9n7dd+kr5gVkArs/mkudsAwWCgnsPE6uk4LNvo9vu+Bl+1orOyFj1txpDp8XW3hF4OARvpIPV34I3232kckxiJaHV9Xo7TiG9yAdyChP/UK0HQ41Y9Ka9vBWeK9muPEeftKtjLfvPaw3LShvNvmqwPKdw94Kq0EQCF/2VgADuJu9vvN+rEZSQJnRlPLhn22A7qpdZ8knKzHw34uTHIRYW0kDet4Dd8f6M23TDWLrPPLGg1U8pDdZhxKATwgPXOzpC8LtJ+Lsgzz54CKqyp70JPSkduikVfZaKcvHXzPe9ZP/cIpwvUjcZ0Qsq+w1sC+tFTrlYcS1gVXz1btIs89erx82M/pzWBAi3SQIV7Pnzfl23uUMWD3m9/HDViVQh0FeGDiNMfMvEz+pGiv/sgHK+9B+88fj/D17vlpB7PW1EQ8Zi7g8ve25DKbxl5Q82Q60yXl05yqIJCdUYC3a3jgvaKP28LNpKtYQcOmoilFAZcQ6gON0FoO4LkmyNHSeK1VtGfav/06KaPPgi3wZwjgQUjHqQgwJqyspt8To+JPGHO05WMJscT8KSAFEYmU/h50vvNkwCv+qKgv2jzd4weY05HbDUK0G52zAsk19dwqk0wjBvIZGhLxoaW8z44ErCrNiLINx5JmWKwmtb1EfxNPRrWGbfUAXcR+EjMEpLYTJh6GTjzFm098B2z5+z3W/xC9DzZVBzz7eaA==; bm_sv=D59ECCE2FC5822A367257A45FF2952D8~YAAQKUw5F1qzPxygAQAArbFqTACUKwpzB3qB0t8qNNxYnvYMSx5uOUYvWQSOTfpFhVvyf7Pcy+idW42uezMAmRyNB8xmei20CvGIQAKhzLkkSX/Iwi6pwth+OrtLQoLdl4QlXtC9S7r8zeenpJHVqaMH/H11sBuXau4Z3+QswlNsg3ZxogkvUKHwKT+4dUdq32hEa60DC5lJ3x1GFq1j2eaX+H6of9AIBJ/0yemXIRPA0mMOcFb4eSyA+BEsXz52~1; RT="z=1&dm=arket.com&si=e8e50e42-a240-409c-b5d1-4f121da4d98f&ss=mte20nmu&sl=6&tt=9w6&bcn=%2F%2F684d0d46.akstat.io%2F"',
        }

        last_error = None
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                response = requests.get(
                    url,
                    cookies=cookies,
                    headers=headers,
                    # proxies={"http": PROXY, "https": PROXY},
                    timeout=20,
                    impersonate="chrome124",
                )
                if response.status_code == 403:
                    get_bm_s_cookie(url)
                    with open("bm_s_cookie.txt", "r") as f:
                        cookies["bm_s"] = f.read().strip()

                if response.status_code != 200:
                    raise ValueError(
                        f"Failed to fetch the product page. Status code: {response.status_code}"
                    )

                html = HTMLParser(response.text)
                scripts = html.css('script[type="application/ld+json"]')
                if not scripts:
                    print(response.text)
                    raise ValueError("No JSON-LD product data found on the page.")

                payload = json.loads(scripts[0].text())
                product_graph = payload.get("@graph", [])
                if not product_graph:
                    raise ValueError("JSON-LD product graph is empty.")

                source = next(
                    (item for item in product_graph if item.get("@type") == "Product"),
                    None,
                )
                if source is None:
                    raise ValueError("No Product entry found in the JSON-LD data.")

                break
            except (CurlError, ValueError, json.JSONDecodeError) as exc:
                last_error = exc
                if attempt == MAX_RETRIES:
                    raise
                print(
                    f"[yellow]Arket attempt {attempt}/{MAX_RETRIES} failed: {exc}. Retrying...[/yellow]"
                )
                print(
                    f"[yellow]Waiting {PROXY_SPIN_TIMEOUT} seconds before retrying...[/yellow]"
                )
                time.sleep(PROXY_SPIN_TIMEOUT)

        images = source.get("image") or []
        if not images:
            raise ValueError("No image URLs found for the product.")

        image_url = str(images[0]).split("?")[0]
        image = _attempt_download(image_url, use_http2=True, proxy=PROXY)
        if not isinstance(image, (bytes, bytearray)):
            raise TypeError("Downloaded image payload is invalid.")

        os.makedirs("images", exist_ok=True)
        sku = source.get("sku") or "arket_product"
        image_filename = f"arket_product_{sku}.jpg"
        image_path = os.path.join("images", image_filename)
        with open(image_path, "wb") as f:
            f.write(image)

        thumb_filename = create_thumbnail(image_path)
        public_image_url = f"{BASE_URL.rstrip('/')}{STATIC_ROUTE}/{image_filename}"
        thumbnail_url = (
            f"{BASE_URL.rstrip('/')}{STATIC_ROUTE}/{thumb_filename}"
            if thumb_filename
            else ""
        )

        product_data = {
            "id": sku,
            "content_type": "product",
            "source": "Arket",
            "title": source.get("name", "Unknown product"),
            "price": source.get("offers", [{}])[0].get("price", "N/A"),
            "brand": source.get("brand", {}).get("name", "Unknown brand"),
            "image_url": public_image_url,
            "thumbnail_url": thumbnail_url,
            "url": url,
        }

        print(product_data)
        return product_data

    except CurlError as exc:
        print(f"[red]Request error while fetching Arket product: {exc}[/red]")
        return {"error": str(exc), "source": "Arket", "url": url}
    except (
        ValueError,
        TypeError,
        KeyError,
        IndexError,
        json.JSONDecodeError,
        OSError,
    ) as exc:
        print(f"[red]Failed to parse or save Arket product: {exc}[/red]")
        return {"error": str(exc), "source": "Arket", "url": url}
    except Exception as exc:
        print(f"[red]Unexpected Arket error: {exc}[/red]")
        return {"error": str(exc), "source": "Arket", "url": url}


if __name__ == "__main__":
    get_arket_product(
        "https://www.arket.com/en-gb/product/relaxed-cotton-jacket-dark-mole-1348122003/"
    )
