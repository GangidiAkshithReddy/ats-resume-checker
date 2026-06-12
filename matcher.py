import re
from collections import Counter

# A reasonably broad stopword list (avoids needing nltk downloads at runtime)
STOPWORDS = set("""
a about above after again against all am an and any are aren't as at be because been before
being below between both but by can't cannot could couldn't did didn't do does doesn't doing
don't down during each few for from further had hadn't has hasn't have haven't having he he'd
he'll he's her here here's hers herself him himself his how how's i i'd i'll i'm i've if in into
is isn't it it's its itself let's me more most mustn't my myself no nor not of off on once only
or other ought our ours ourselves out over own same shan't she she'd she'll she's should
shouldn't so some such than that that's the their theirs them themselves then there there's
these they they'd they'll they're they've this those through to too under until up very was
wasn't we we'd we'll we're we've were weren't what what's when when's where where's which while
who who's whom why why's with won't would wouldn't you you'd you'll you're you've your yours
yourself yourselves
""".split())

# Generic resume filler words that aren't useful as "skills" keywords
GENERIC_WORDS = set("""
experience experienced work worked working team teams company companies role roles year years
responsible responsibility responsibilities including include included strong excellent ability
abilities proven track record results driven environment environments etc using used use uses
various duties tasks task job jobs candidate candidates ideal preferred preference required
requirements requirement plus skill skills knowledge understanding good great new like e.g i.e
looking seeking apply application opportunity opportunities position positions across within
across must nice based help helping ensure ensuring across develop developing develops growing
grow self able well also etc related similar provide provides providing support supporting
benefits benefit join joining culture cultures fast paced passion passionate
""".split())


def tokenize(text):
    text = text.lower()
    # keep words, numbers, and tech terms with + # . / -
    tokens = re.findall(r"[a-z0-9][a-z0-9\+\#\.\-/]*[a-z0-9]|[a-z0-9]", text)
    return tokens


def extract_keywords(text, top_n=40):
    tokens = tokenize(text)
    filtered = [
        t for t in tokens
        if t not in STOPWORDS
        and t not in GENERIC_WORDS
        and len(t) > 1
        and not t.isdigit()
    ]

    counts = Counter(filtered)

    # also extract bigrams (e.g. "machine learning", "power bi")
    bigrams = []
    for i in range(len(filtered) - 1):
        bigram = f"{filtered[i]} {filtered[i+1]}"
        bigrams.append(bigram)
    bigram_counts = Counter(bigrams)

    # combine, weighting bigrams slightly higher since they're more specific
    combined = counts.copy()
    for bg, c in bigram_counts.items():
        if c > 1:
            combined[bg] = c + 1

    return [word for word, _ in combined.most_common(top_n)]


def calculate_match(resume_text, jd_text, top_n=40):
    resume_clean = resume_text.lower()
    jd_keywords = extract_keywords(jd_text, top_n=top_n)

    matched = []
    missing = []

    for kw in jd_keywords:
        if kw in resume_clean:
            matched.append(kw)
        else:
            missing.append(kw)

    if jd_keywords:
        score = round((len(matched) / len(jd_keywords)) * 100, 1)
    else:
        score = 0.0

    return {
        "score": score,
        "matched": matched,
        "missing": missing,
        "total_keywords": len(jd_keywords),
    }
