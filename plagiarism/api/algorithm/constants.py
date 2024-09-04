import pickle


def setup_environment():
    try:
        with open("useragent.txt", "r") as file:
            user_agents = file.read().split("\n")
    except FileNotFoundError:
        user_agents = ["Mozilla/5.0"]

    return user_agents


POOL_SIZE = 8
NGRAM_SIZE = 4

USER_AGENTS = setup_environment()

with open("api/algorithm/vectorizer.pkl", "rb") as file:
    TF_IDF_VECTORIZER = pickle.load(file)
