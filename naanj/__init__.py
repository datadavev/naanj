"""
Translating the NAAN registry to JSON
"""
import sys
import re
import logging
import requests
import json
import datetime
import dateparser
import asyncio
import aiohttp
import naanj.anvl

AUTHORITY_SOURCE = "https://n2t.net/e/pub/naan_registry.txt"
STATUS_THREADS = 20

_L = logging.getLogger("naanj")

JSON_TIME_FORMAT = "%Y-%m-%dT%H:%M:%S%z"
"""datetime format string for generating JSON content
"""


def datetimeToJsonStr(dt):
    if dt is None:
        return None
    if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
        # Naive timestamp, convention is this must be UTC
        return f"{dt.strftime(JSON_TIME_FORMAT)}Z"
    return dt.strftime(JSON_TIME_FORMAT)


def _jsonConverter(o):
    if isinstance(o, datetime.datetime):
        return datetimeToJsonStr(o)
    return o.__str__()


class Naans(object):
    def __init__(self):
        self.header = {}
        self.naa = []

    def load(self, src=AUTHORITY_SOURCE):
        response = requests.get(src, timeout=5)
        if not response.status_code == 200:
            raise ValueError(f"Authority returned status code: {response.status_code}")
        for block in naanj.anvl.parseBlocks(response.text):
            k0 = list(block.keys())[0]
            if k0 == "erc":
                self.addHeader(block["erc"])
            elif k0 == "naa":
                self.addNaa(block["naa"])
            else:
                _L.warning("Unprocessed block: %s", k0)

    def addHeader(self, block):
        self.header = block
        self.header["when"] = dateparser.parse(
            block["when"],
            settings={
                "RETURN_AS_TIMEZONE_AWARE": True,
                "TIMEZONE": "UTC",
            },
        )
        self.header["num_entries"] = 0

    def _splitEq(self, e):
        parts = re.split(r"\(=\)", e)
        res = []
        for p in parts:
            p = p.strip()
            if len(p) > 0:
                res.append(p)
        return res

    def _splitPipe(self, e):
        parts = re.split(r"\|", e)
        res = []
        for p in parts:
            res.append(p.strip())
        return res

    def _asUrl(self, e):
        if e.find("http") == 0:
            return e
        return f"http://{e}"

    def addNaa(self, block):
        whop = self._splitEq(block["who"])
        who = {"literal": whop[0], "abbrev": whop[-1]}
        if len(whop) > 2:
            who["en"] = whop[1]
        howp = self._splitPipe(block["how"])
        how = {
            "org_type": howp[0],
            "policy_summary": howp[1],
            "start_year": int(howp[2]),
            "policy_url": None,
        }
        if len(howp[3]) > 0:
            how["policy_url"] = howp[3]
        naa = {
            "who": who,
            "what": block["what"],
            "when": dateparser.parse(
                block["when"],
                settings={"RETURN_AS_TIMEZONE_AWARE": True, "TIMEZONE": "UTC"},
            ),
            "where": {
                "url": self._asUrl(block["where"]),
                "status": None,
                "timestamp": None,
                "msg": None,
            },
            "how": how,
        }
        self.naa.append(naa)
        self.header["num_entries"] = self.header.get("num_entries", 0) + 1

    def __str__(self):
        return json.dumps(self.header, indent=2, default=_jsonConverter)

    def __iter__(self):
        return enumerate(self.naa)


    def asJson(self):
        return json.dumps({"erc":self.header,"naa":self.naa}, indent=2, default=_jsonConverter)

    def checkSources(self):
        async def checkStatus(idx, url, session):
            try:
                async with session.get(
                    url,
                    timeout=aiohttp.ClientTimeout(
                        total=10, sock_connect=5, sock_read=5
                    ),
                ) as response:
                    status = response.status
                    _L.debug("%s: %s", status, response.url)
                    tstamp = datetime.datetime.now().astimezone(datetime.timezone.utc)
                    return (idx, status, tstamp, None)
            except Exception as e:
                _L.error(e)
                tstamp = datetime.datetime.now().astimezone(datetime.timezone.utc)
                return idx, 0, tstamp, str(e)

        async def run(urls):
            tasks = []
            async with aiohttp.ClientSession() as session:
                i = 0
                for url in urls:
                    task = asyncio.ensure_future(checkStatus(i, url, session))
                    i += 1
                    tasks.append(task)
                responses = asyncio.gather(*tasks)
                await responses
            return responses

        urls = []
        for entry in self.naa:
            urls.append(entry["where"]["url"])
        loop = asyncio.get_event_loop()
        asyncio.set_event_loop(loop)
        task = asyncio.ensure_future(run(urls))
        loop.run_until_complete(task)
        for result in task.result().result():
            upd = {
                "status": result[1],
                "timestamp": result[2],
                "msg": result[3]
            }
            idx = result[0]
            self.naa[idx]["where"].update(upd)


def main():
    logging.basicConfig(level=logging.DEBUG)
    naans = Naans()
    naans.load()
    print(naans)
    naans.checkSources()
    print(naans.asJson())


if __name__ == "__main__":
    sys.exit(main())
