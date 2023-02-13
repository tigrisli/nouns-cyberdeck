import requests

# Set the query to fetch the seed data from the Nouns subgraph API
url = "https://api.thegraph.com/subgraphs/name/nounsdao/nouns-subgraph"
query = '''
query {
  auctions(orderDirection: desc, orderBy: startTime) {
    id
    amount
    startTime
    endTime
    bids(orderDirection: desc,orderBy:amount) {
      id
      amount
      blockNumber
      txIndex
      noun {
        id
        seed {
          background
          body
          accessory
          head
          glasses
        }
      }
    }
  }
}
'''



response = requests.post(url, json={'query': query})

if response.status_code == 200:
    result = response.json()
    print(result)
else:
    raise Exception("Query failed to run by returning code of {}. {}".format(response.status_code, response.text))