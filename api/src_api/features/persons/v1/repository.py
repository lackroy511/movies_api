# Запрос на поиск фильмов по персоне
# {
#   "query": {
#     "bool": {
#       "should": [
#         {
#           "nested": {
#             "path": "directors",
#             "query": {
#               "term": { "directors.id": "PERSON_ID" }
#             }
#           }
#         },
#         {
#           "nested": {
#             "path": "actors",
#             "query": {
#               "term": { "actors.id": "PERSON_ID" }
#             }
#           }
#         },
#         {
#           "nested": {
#             "path": "writers",
#             "query": {
#               "term": { "writers.id": "PERSON_ID" }
#             }
#           }
#         }
#       ],
#       "minimum_should_match": 1
#     }
#   }
# }