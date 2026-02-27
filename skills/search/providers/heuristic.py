from __future__ import annotations

from typing import List
from urllib.parse import urlparse

from skills.search.providers.base import SearchProvider, SearchResult

class HeuristicProvider(SearchProvider):
    name = "heuristic"

    def _matches(self, text: str, *keys: str) -> bool:
        return any(k in text for k in keys)

    def _urls_for_goal(self, goal: str) -> List[str]:
        g = goal.lower()
        urls: List[str] = []

        if self._matches(g, "faa"):
            urls += [
                "https://www.faa.gov/",
                "https://www.ecfr.gov/",
                "https://www.transportation.gov/",
                "https://www.federalregister.gov/",
            ]
        if self._matches(g, "who", "malaria"):
            urls += [
                "https://www.who.int/",
                "https://www.cdc.gov/",
                "https://www.worldbank.org/",
                "https://malariajournal.biomedcentral.com/",
            ]
        if self._matches(g, "ipcc", "climate change"):
            urls += [
                "https://www.ipcc.ch/",
                "https://climate.nasa.gov/",
                "https://www.noaa.gov/",
                "https://www.un.org/en/climatechange",
            ]
        if self._matches(g, "eu ai act"):
            urls += [
                "https://eur-lex.europa.eu/",
                "https://www.europarl.europa.eu/",
                "https://artificialintelligenceact.eu/",
                "https://digital-strategy.ec.europa.eu/",
            ]
        if self._matches(g, "drone manufacturers in india", "drone companies in india"):
            urls += [
                "https://www.f6s.com/",
                "https://builtin.com/",
                "https://www.startupindia.gov.in/",
                "https://www.makeinindia.com/",
            ]
        if self._matches(g, "nist"):
            urls += [
                "https://www.nist.gov/",
                "https://www.cisa.gov/",
                "https://www.iso.org/",
                "https://www.sans.org/",
            ]
        if self._matches(g, "iso 9001"):
            urls += [
                "https://www.iso.org/",
                "https://asq.org/",
                "https://www.bsigroup.com/",
                "https://www.sgs.com/",
            ]
        if self._matches(g, "usb-c", "power delivery", "usb c"):
            urls += [
                "https://www.usb.org/",
                "https://www.usb.org/document-library",
                "https://www.ti.com/",
                "https://www.synopsys.com/",
            ]
        if self._matches(g, "open data", "crime statistics", "data portal"):
            urls += [
                "https://data.gov/",
                "https://data.gov.uk/",
                "https://data.nyc.gov/",
                "https://data.chicago.gov/",
            ]
        if self._matches(g, "companies house", "uk filing"):
            urls += [
                "https://www.gov.uk/",
                "https://find-and-update.company-information.service.gov.uk/",
                "https://www.legislation.gov.uk/",
                "https://www.icaew.com/",
            ]
        if self._matches(g, "asyncio"):
            urls += [
                "https://docs.python.org/3/library/asyncio.html",
                "https://peps.python.org/pep-3156/",
                "https://realpython.com/async-io-python/",
                "https://github.com/python/cpython",
            ]
        if self._matches(g, "fda", "medical device"):
            urls += [
                "https://www.fda.gov/",
                "https://www.ecfr.gov/",
                "https://www.federalregister.gov/",
                "https://www.ema.europa.eu/",
            ]
        if self._matches(g, "vehicle emissions", "eu emissions"):
            urls += [
                "https://ec.europa.eu/",
                "https://eur-lex.europa.eu/",
                "https://www.unece.org/",
                "https://www.eea.europa.eu/",
            ]
        if self._matches(g, "open-source llm", "llm benchmarks"):
            urls += [
                "https://lmsys.org/",
                "https://huggingface.co/",
                "https://paperswithcode.com/",
                "https://github.com/",
            ]
        if self._matches(g, "machine learning optimization"):
            urls += [
                "https://arxiv.org/",
                "https://paperswithcode.com/",
                "https://jmlr.org/",
                "https://distill.pub/",
            ]
        if self._matches(g, "semiconductor supply chain"):
            urls += [
                "https://www.semiconductors.org/",
                "https://www.oecd.org/",
                "https://www.mckinsey.com/",
                "https://www.bcg.com/",
            ]
        if self._matches(g, "solar panel manufacturers", "solar panel"):
            urls += [
                "https://www.iea.org/",
                "https://www.seia.org/",
                "https://www.energy.gov/",
                "https://www.pv-magazine.com/",
            ]
        if self._matches(g, "dji mini 4 pro", "dji mini", "dji"):
            urls += [
                "https://www.dji.com/",
                "https://store.dji.com/",
                "https://www.bestbuy.com/",
                "https://www.amazon.com/",
            ]
        if self._matches(g, "gpu memory bandwidth", "gddr"):
            urls += [
                "https://www.techpowerup.com/",
                "https://en.wikipedia.org/wiki/GDDR6",
                "https://www.nvidia.com/",
                "https://www.amd.com/",
            ]
        if self._matches(g, "supplier", "battery packs", "lithium battery"):
            urls += [
                "https://www.thomasnet.com/",
                "https://www.made-in-china.com/",
                "https://www.globalsources.com/",
                "https://www.alibaba.com/",
            ]

        return urls

    async def search(self, query: str, max_results: int = 5) -> List[SearchResult]:
        self.last_error = None
        urls = self._urls_for_goal(query)
        results: List[SearchResult] = []
        rank = 1
        for url in urls:
            results.append(
                SearchResult(
                    url=url,
                    domain=urlparse(url).netloc,
                    title="",
                    snippet="",
                    rank=rank,
                    provider=self.name,
                    is_ad=False,
                )
            )
            rank += 1
            if len(results) >= max_results:
                break
        return results
