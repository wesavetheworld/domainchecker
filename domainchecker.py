#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import argparse
import codecs
import csv
import json
import urllib2
from termcolor import colored


def bad_keyword(keyword):
    chars = set('.,\'&/$%@#')
    if any((c in chars) for c in keyword):
        return True
    else:
        return False


def read_keywords(filename):
    keywords = []

    ignored = open("ignored.txt", "a")

    with codecs.open(filename, "rU", "utf-16") as f:
#    with codecs.open(filename, "rU", "utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        reader.next()  # skipping header
        for row in reader:
            keyword = row[1]
            if not bad_keyword(keyword):
                keywords.append(row[1])
            else:
                ignored.write(keyword)
                ignored.write("\n")

        ignored.close()

        return keywords


def domainr_info_json(domainname):
    requesturl = "http://www.domai.nr/api/json/info?q="
    requesturl += domainname
    request = urllib2.Request(requesturl)
    request.add_header("User-Agent", "Mozilla/2.0 (compatible; MSIE 3.0; Windows 95)")
    opener = urllib2.build_opener()
    response = opener.open(request).read()
    objs = json.loads(response)
    return objs


def is_taken(domainr_json):
    return domainr_json["availability"] == "taken"


def concatenation(keyword, symbol):
    return symbol.join(keyword.lower().split())


def prepare_domains(keyword, tld):
    domains = []
    if ' ' in keyword:
        for symbol in ['', '-']:
            domains.append(
                '{0}{1}'.format(concatenation(keyword, symbol), tld)
            )
    else:
        domains.append('{0}{1}'.format(keyword, tld))
    return domains

def fetch_single(domain):
    try:
        req = domainr_info_json(domain)
    except Exception as e:
        print(colored('Error "{0}" occurred when requesting '
                      '{1} domain'.format(e, domain), 'red'))
        return

    if is_taken(req):
        print(colored('Domain Taken --------- : {0}'.format(domain), 'red'))
        return False
    else:
        print(colored('Domain Free ---------- : {0}'.format(domain), 'green'))
        return True

def fetch_status(keywords):
    rows = [["Keyword", "com", "net", "org", "com hyphen", "net hyphen", "org hyphen"]]

    for keyword in keywords:
        row = [keyword]
        for tld in [".com", ".net", ".org"]:
            domains = prepare_domains(keyword, tld)
            for domain in domains:
                result = fetch_single(domain)
                if result is True:
                    row.append("XXXXX")
                elif result is False:
                    row.append(keyword)

        rows.append(row)
    return rows


def write_result(filename, rows):
    with open(filename, "wb") as res:
        writer = csv.writer(res, delimiter="\t")
        writer.writerows(rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="domainchecker", version="0.2")
    parser.add_argument("--input", "-i", type=str)
    parser.add_argument("--output", "-o", type=str)

    args = parser.parse_args()

    keywords = read_keywords(args.input)

    write_result(args.output, fetch_status(keywords))
