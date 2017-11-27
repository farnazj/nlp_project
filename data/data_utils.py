import numpy as np
import data.dataset as dataset
import gzip
import tqdm

PATH_EMB = "./askubuntu/vector/vectors_pruned.200.txt.gz"
PATH_TEXT = "./askubuntu/text_tokenized.txt.gz"
PATH_DEV = "./askubuntu/dev.txt"
PATH_TEST = "./askubuntu/test.txt"
PATH_TRAIN = "./askubuntu/train_random.txt"

PATH_EMB_SAVE = './embedding.pickle'
PATH_ID2DATA_SAVE = './id2data.pickle'
PATH_MAXES_SAVE = './maxes.txt'


EMB_LEN = 200
MAX_BODY_LEN = 100

def getEmbeddingTensor():
    word2idx = {}
    embedding_tensor = []
    embedding_tensor.append(np.zeros(EMB_LEN))

    with gzip.open(PATH_EMB) as gfile:
        for i, line in enumerate(gfile, start=1):
            word, emb = line.split()[0], line.split()[1:]
            vector = [float(x) for x in emb]
            embedding_tensor.append(vector)
            word2idx[word] = i
    embedding_tensor = np.array(embedding_tensor, dtype=np.float32)
    return embedding_tensor, word2idx

def getId2Data(word2idx):
    id2data = {}
    max_title = 0
    max_body = 0

    with gzip.open(PATH_TEXT) as gfile:
        for line in tqdm.tqdm(gfile):
            qid, qtitle, qbody = line.split('\t')
            title = qtitle.split()
            body = qbody.split()

            title2iarr = [word2idx[x] for x in title if x in word2idx]
            body2iarr = []

            count = 0
            for word in body:
                if word in word2idx:
                    if count >= MAX_BODY_LEN:
                        break
                    body2iarr.append(word2idx[word])
                    count += 1

            if max_title < len(title2iarr):
                max_title = len(title2iarr)


            if len(title2iarr) != 0 and len(body2iarr) != 0:
                id2data[qid] = ((title2iarr, len(title2iarr)), (body2iarr, len(body2iarr) ))

    return id2data, max_title, MAX_BODY_LEN


def loadDataset(args):
    print "\nLoading data..."
    embedding_tensor, word2idx = getEmbeddingTensor()
    id2data, max_title, max_body = getId2Data(word2idx)

    args.embedding_dim = embedding_tensor.shape[1]

    if args.train:
        train_data = dataset.AskUbuntuDataset(PATH_TRAIN, id2data, max_title, max_body, True)
    else:
        train_data = None
    if args.dev:
        dev_data = dataset.AskUbuntuDataset(PATH_DEV, id2data, max_title, max_body, False)
    else:
        dev_data = None
    if args.test:
        test_data = dataset.AskUbuntuDataset(PATH_TEST, id2data, max_title, max_body, False)
    else:
        test_data = None

    return train_data, dev_data, test_data, embedding_tensor
