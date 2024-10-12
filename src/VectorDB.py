import pandas as pd
import os
import ast
from scipy import spatial
from typing import Union
class vectorDB:
    def __init__(self,embedding,save_path):
        self.save_path = save_path
        self.embedding = embedding
        self.chunks=[]

    def store(self,text: Union[str, list], history):
        #当text为字符串时的处理
        if isinstance(text, str):
            if text == '':
                return
            vector = self.embedding.embed_documents([text])
            df = pd.DataFrame({"text": str(history), "embedding": vector})
        #当text为list的处理
        elif isinstance(text, list):
            print(str(text[0]))
            if len(text) == 0:
                return
            vector = self.embedding.embed_documents(str(text[0]))
            df = pd.DataFrame({"text": history, "embedding": vector})
        else:
            raise TypeError('text must be str or list')
        df.to_csv(self.save_path, mode='a', header=not os.path.exists(self.save_path), index=False)

    def query(self, text: str, top_n: int, threshold: float = 0.8):
        print("begin query")
        if text == '':
            return [''], ['']
        #计算余弦相似度，越接近1说明越相似
        relatedness_fn=lambda x, y: 1 - spatial.distance.cosine(x, y)

        # Load embeddings data
        if not os.path.isfile(self.save_path):
            return [''], ['']
        df = pd.read_csv(self.save_path)
        row = df.shape[0]
        top_n = min(top_n, row)
        df['embedding'] = df['embedding'].apply(ast.literal_eval)
        print(text[5:])
        # Make query
        query_embedding = self.embedding.embed_documents([text[5:]])[0]
        strings_and_relatednesses = [
            (row["text"], relatedness_fn(query_embedding, row["embedding"]))
            for i, row in df.iterrows()
        ]
        
        # Rank
        final_strings=['']
        final_relatednesses=['']
        strings_and_relatednesses.sort(key=lambda x: x[1], reverse=True)
        strings, relatednesses = zip(*strings_and_relatednesses)
        for i in range(len(relatednesses)):
            if relatednesses[i] < threshold:
                break
            else:
                final_strings.append(strings[i])
                final_relatednesses.append(relatednesses[i])
        return final_strings[:min(i+1, top_n)], final_relatednesses[:min(i+1, top_n)]