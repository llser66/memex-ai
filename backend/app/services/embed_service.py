from sentence_transformers import SentenceTransformer


model = SentenceTransformer(
    "BAAI/bge-small-zh-v1.5"
)



def generate_embedding(text):

    vector = model.encode(
        text
    )


    return vector.tolist()