from app.database.chroma import collection



def search(query):

    result = collection.query(

        query_texts=[
            query
        ],

        n_results=3
    )


    return result