def insert_vertices(insert_vertices, client):
    for query in insert_vertices:
        print("\tRunning this Gremlin query:\n\t{0}\n".format(query))
        callback = client.submitAsync(query)
        if callback.result() is not None:
            print("\tInserted this vertex:\n\t{0}\n".format(callback.result().one()))
        else:
            print("Something went wrong with this query: {0}".format(query))
    print("\n")

def insert_edges(insert_edges, client):
    for query in insert_edges:
        print("\tRunning this Gremlin query:\n\t{0}\n".format(query))
        callback = client.submitAsync(query)
        if callback.result() is not None:
            print("\tInserted this edge:\n\t{0}\n".format(callback.result().one()))
        else:
            print("Something went wrong with this query:\n\t{0}".format(query))
    print("\n")