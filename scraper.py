"""
Berlin Job Tracker – Mateus Andery Rissoni
==========================================
Busca diária de vagas em Berlim alinhadas ao perfil:
- Idiomas: inglês, espanhol, português
- Áreas: políticas públicas, pesquisa, cooperação internacional,
  governança, América Latina, NGO, think tank
- Sem requisito de alemão fluente
"""

import json
import os
import time
import hashlib
import datetime
import requests
from bs4 import BeautifulSoup
import feedparser

# ── Configuração ──────────────────────────────────────────────────────────────

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    )
}

DATA_FILE = "jobs_data.json"

# Palavras-chave de busca (combinações usadas nas fontes RSS/URL)
SEARCH_QUERIES = [
    "policy research berlin english",
    "international cooperation berlin english",
    "student assistant berlin english policy",
    "NGO intern berlin english spanish",
    "think tank berlin english",
    "governance berlin english intern",
    "latin america berlin english",
    "communications assistant berlin english research",
    "werkstudent berlin english policy",
    "junior policy advisor berlin english",
]

# Palavras que devem aparecer no título ou descrição para qualificar a vaga
INCLUDE_KEYWORDS = [
    "english", "policy", "research", "international", "governance",
    "cooperation", "ngo", "think tank", "latin", "communications",
    "assistant", "intern", "analyst", "development", "sustainability",
    "bilingual", "spanish", "portuguese", "multilingual"
]

# Palavras que desqualificam a vaga (requerem alemão fluente como condição)
EXCLUDE_KEYWORDS = [
    "deutschkenntnisse erforderlich",
    "fließend deutsch",
    "muttersprachliche deutschkenntnisse",
    "deutsch als muttersprache",
    "c1 deutsch erforderlich",
    "c2 deutsch",
]

# ── Fontes RSS ────────────────────────────────────────────────────────────────

def get_indeed_rss(query: str) -> list[dict]:
    """Busca vagas via RSS do Indeed Alemanha."""
    q = query.replace(" ", "+")
    url = f"https://de.indeed.com/rss?q={q}&l=Berlin&radius=25&lang=en"
    try:
        feed = feedparser.parse(url)
        results = []
        for entry in feed.entries[:8]:
            results.append({
                "title": entry.get("title", ""),
                "company": entry.get("author", "Unknown"),
                "description": BeautifulSoup(
                    entry.get("summary", ""), "html.parser"
                ).get_text()[:400],
                "url": entry.get("link", ""),
                "source": "Indeed",
                "location": "Berlin",
            })
        return results
    except Exception as e:
        print(f"  [Indeed RSS] Erro: {e}")
        return []


def get_euractiv_jobs() -> list[dict]:
    """Busca vagas no Euractiv Jobs (política europeia, inglês)."""
    url = "https://jobs.euractiv.com/feed/?location=Germany"
    try:
        feed = feedparser.parse(url)
        results = []
        for entry in feed.entries[:10]:
            results.append({
                "title": entry.get("title", ""),
                "company": entry.get("author", "Unknown"),
                "description": BeautifulSoup(
                    entry.get("summary", ""), "html.parser"
                ).get_text()[:400],
                "url": entry.get("link", ""),
                "source": "Euractiv Jobs",
                "location": "Germany/Berlin",
            })
        return results
    except Exception as e:
        print(f"  [Euractiv] Erro: {e}")
        return []


def get_impactpool_jobs() -> list[dict]:
    """Busca vagas no ImpactPool (ONGs e cooperação internacional)."""
    url = "https://www.impactpool.org/jobs/rss?country=Germany&language=English"
    try:
        feed = feedparser.parse(url)
        results = []
        for entry in feed.entries[:10]:
            results.append({
                "title": entry.get("title", ""),
                "company": entry.get("author", "Unknown"),
                "description": BeautifulSoup(
                    entry.get("summary", ""), "html.parser"
                ).get_text()[:400],
                "url": entry.get("link", ""),
                "source": "ImpactPool",
                "location": "Germany",
            })
        return results
    except Exception as e:
        print(f"  [ImpactPool] Erro: {e}")
        return []


def get_devex_jobs() -> list[dict]:
    """Busca vagas no Devex (desenvolvimento internacional)."""
    url = "https://www.devex.com/jobs/search.rss?country=276&keyword=policy"
    try:
        feed = feedparser.parse(url)
        results = []
        for entry in feed.entries[:10]:
            results.append({
                "title": entry.get("title", ""),
                "company": entry.get("author", "Unknown"),
                "description": BeautifulSoup(
                    entry.get("summary", ""), "html.parser"
                ).get_text()[:400],
                "url": entry.get("link", ""),
                "source": "Devex",
                "location": "Germany",
            })
        return results
    except Exception as e:
        print(f"  [Devex] Erro: {e}")
        return []


# ── Filtros ───────────────────────────────────────────────────────────────────

def is_relevant(job: dict) -> bool:
    """Retorna True se a vaga passa pelos filtros de inclusão e exclusão."""
    text = (
        job.get("title", "") + " " + job.get("description", "")
    ).lower()

    # Pelo menos uma palavra-chave de inclusão deve estar presente
    has_include = any(kw in text for kw in INCLUDE_KEYWORDS)

    # Nenhuma palavra de exclusão pode estar presente
    has_exclude = any(kw in text for kw in EXCLUDE_KEYWORDS)

    return has_include and not has_exclude


def score_job(job: dict) -> int:
    """Pontua a vaga de 0 a 100 com base na relevância para o perfil."""
    text = (
        job.get("title", "") + " " + job.get("description", "")
    ).lower()

    score = 0
    high_value = [
        "latin america", "policy", "research", "governance",
        "international cooperation", "ngo", "think tank",
        "public policy", "english", "spanish", "portuguese",
        "giz", "undp", "development", "sustainability",
        "communications", "intern", "student assistant"
    ]
    for kw in high_value:
        if kw in text:
            score += 7

    return min(score, 100)


# ── ID único por vaga ─────────────────────────────────────────────────────────

def job_id(job: dict) -> str:
    key = (job.get("title", "") + job.get("url", "")).encode()
    return hashlib.md5(key).hexdigest()[:12]


# ── Pipeline principal ────────────────────────────────────────────────────────

def fetch_all_jobs() -> list[dict]:
    all_jobs = []

    print("🔍 Buscando Indeed RSS...")
    for query in SEARCH_QUERIES[:5]:  # limitar para não sobrecarregar
        jobs = get_indeed_rss(query)
        all_jobs.extend(jobs)
        time.sleep(1)

    print("🔍 Buscando Euractiv Jobs...")
    all_jobs.extend(get_euractiv_jobs())
    time.sleep(1)

    print("🔍 Buscando ImpactPool...")
    all_jobs.extend(get_impactpool_jobs())
    time.sleep(1)

    print("🔍 Buscando Devex...")
    all_jobs.extend(get_devex_jobs())

    # Filtrar e pontuar
    filtered = []
    seen = set()
    for job in all_jobs:
        jid = job_id(job)
        if jid in seen:
            continue
        seen.add(jid)
        if is_relevant(job):
            job["id"] = jid
            job["score"] = score_job(job)
            job["found_date"] = datetime.date.today().isoformat()
            filtered.append(job)

    # Ordenar por pontuação
    filtered.sort(key=lambda x: x["score"], reverse=True)
    return filtered


def load_existing() -> dict:
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"jobs": [], "last_updated": None, "history": []}


def save_data(data: dict):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def run():
    print(f"\n{'='*50}")
    print(f"  Berlin Job Tracker – {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print(f"{'='*50}\n")

    existing = load_existing()
    existing_ids = {j["id"] for j in existing.get("jobs", [])}

    new_jobs = fetch_all_jobs()

    # Identificar novas vagas
    truly_new = [j for j in new_jobs if j["id"] not in existing_ids]
    print(f"\n✅ {len(new_jobs)} vagas relevantes encontradas")
    print(f"🆕 {len(truly_new)} vagas novas desde a última busca\n")

    # Atualizar dados
    all_jobs = new_jobs  # substituir pela lista atualizada
    existing["jobs"] = all_jobs
    existing["last_updated"] = datetime.datetime.now().isoformat()
    existing["new_today"] = len(truly_new)

    if not existing.get("history"):
        existing["history"] = []
    existing["history"].append({
        "date": datetime.date.today().isoformat(),
        "total": len(all_jobs),
        "new": len(truly_new)
    })
    existing["history"] = existing["history"][-30:]  # manter 30 dias

    save_data(existing)
    print("💾 Dados salvos em jobs_data.json")
    print("🌐 Execute generate_html.py para atualizar o painel\n")


if __name__ == "__main__":
    run()
