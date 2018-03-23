import urllib
import urllib.request
import urllib.error

def download(url, user_agent="gabvilpi", num_retries=2):
    print("Downloading:", url)
    headers = {'User-agent': user_agent}
    request = urllib.request.Request(url=url, headers=headers)
    try:
        html = urllib.request.urlopen(request)
    except urllib.error.URLError as e:
        print("Download error:", e.reason)
        html = None
        if num_retries > 0:
            if hasattr(e, 'code') and 500 <= e.code < 600:
                # Reintento para errores HTTP 5XX
                return download(url, user_agent, num_retries-1)
    return html

url="https://www.filmaffinity.com/es/film161026.html"

page = download(url)
print(page.read())