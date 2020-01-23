#!/usr/bin/env python

import re
import requests

URL = "https://api.github.com/graphql"
TOKEN = "YOUR_GITHUB_TOKEN_HERE"
NUM_PER_REQUEST = 100
FILENAME = "file.csv"

full_list = []

count_query = """
{
  viewer {
    pullRequests(first: 0) {
      totalCount
    }
  }
}
"""


def save_in_file():

    print("Saving in file {}.".format(FILENAME))

    fp = open(FILENAME, "w")
    fp.write("Closed,Closed At,Created At,Upstream URL,State,PR\n")

    for item in full_list:
        closed = item['closed']
        closedAt = item['closedAt']
        createdAt = item['createdAt']
        state = item['state']
        url = item['url']
        src_url = re.sub('/pull/.*', '', url)

        fp.write("{},{},{},{},{},{}\n".format(closed, closedAt, createdAt, src_url, state, url))

    exit()


def pr_query(end_cursor=""):

    # print("value: {}". format(end_cursor))

    if end_cursor == "":
        data = """
        {
        viewer {
            pullRequests(first: """ + str(NUM_PER_REQUEST) + """) {
            totalCount
            nodes {
                state
                closed
                closedAt
                createdAt
                url
                headRepository {
                url
                }
            }
            pageInfo {
                endCursor
                hasNextPage
            }
            }
        }
        }
        """
    else:
        data = """
        {
        viewer {
            pullRequests(first: """ + str(NUM_PER_REQUEST) + """, after: \"""" + str(end_cursor) + """\") {
            totalCount
            nodes {
                state
                closed
                closedAt
                createdAt
                url
                headRepository {
                url
                }
            }
            pageInfo {
                endCursor
                hasNextPage
            }
            }
        }
        }
        """
    return data


def query_data(end_cursor=""):
    aux = pr_query(end_cursor)
    head = {'Authorization': 'bearer {}'.format(TOKEN)}
    r = requests.post(URL, headers=head, json={'query': aux}).json()
    end_cursor = r['data']['viewer']['pullRequests']['pageInfo']['endCursor']
    has_next_page = r['data']['viewer']['pullRequests']['pageInfo']['hasNextPage']

    for rows in r['data']['viewer']['pullRequests']['nodes']:
        full_list.append(rows)

    return has_next_page, end_cursor


def main():
    head = {'Authorization': 'bearer {}'.format(TOKEN)}
    r = requests.post(URL, headers=head, json={'query': count_query}).json()
    total_item = r['data']['viewer']['pullRequests']['totalCount']
    iteration_num = int(total_item / NUM_PER_REQUEST)
    print("Total number of PR's: {}, let's iterate {} times". format(total_item, iteration_num))

    while True:
        # [0] means true or false to has_next_page
        # [1] means the end_cursor
        if 'check_controller' not in locals():
            check_controller = query_data()
        elif check_controller[0]:
            print("Next page ahead, let's do it")
            check_controller = query_data(end_cursor=check_controller[1])
        else:
            save_in_file()

    pass


if __name__ == "__main__":
    main()
