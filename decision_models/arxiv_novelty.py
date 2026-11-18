"""Quick prior-art check: arXiv API keyword searches for each proposal, newest first."""
import json, re, sys, time, urllib.error, urllib.parse, urllib.request
Q = json.load(open(sys.argv[1])); out = {}
for key, queries in Q.items():
    hits = []
    for q in queries:
        url = "https://export.arxiv.org/api/query?" + urllib.parse.urlencode(
            {"search_query": q, "sortBy": "relevance", "max_results": 6})
        for attempt in range(6):
            try:
                x = urllib.request.urlopen(url, timeout=60).read().decode(); break
            except urllib.error.HTTPError as err:
                if err.code != 429: raise
                time.sleep(15 * (attempt + 1))
        else:
            print("  (gave up on query)", q); continue
        for e in x.split("<entry>")[1:]:
            t = " ".join(re.search(r"<title>(.*?)</title>", e, re.S).group(1).split())
            i = re.search(r"<id>(.*?)</id>", e).group(1).split("/")[-1]
            d = re.search(r"<published>(.*?)</published>", e).group(1)[:10]
            hits.append((d, i, t))
        time.sleep(5)
    out[key] = sorted(set(hits), reverse=True)
    print(f"\n## {key}"); [print("  ", *h) for h in out[key][:9]]
json.dump(out, open(sys.argv[2], "w"), indent=1)
