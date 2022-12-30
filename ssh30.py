from sentence_transformers import SentenceTransformer,util
import torch
from dataclasses import dataclass
import numpy


@dataclass
class Dataset_Type:
    """
    body : 文章のリスト.
    embeddings : 各文章の分散表現でTorchのTensor型.
    """
    body:list[str]
    embeddings:torch.Tensor|list[list[int]]|numpy.ndarray



class ssh30:
    """
    query_theme : 検索する内容.
    ds : 検索元となる文章とその埋め込み表現のデータセット.
    model : SentenceTransformerによって読み込み済みのモデル.
    MODEL_NAME : SentenceTransformerによって読み込むためのモデルの名前.\
        Hugging Face上の日本語のSentenceBert(https://huggingface.co/models?language=ja&sort=downloads&search=sentence)\
        を使用.\
        'sonoisa/sentence-bert-base-ja-mean-tokens-v2'は私たちが動作確認で使用したモデル.
    
    modelがMODEL_NAMEより優先される.
    """
    def __init__(self, query_theme:list[str], ds:Dataset_Type, model:SentenceTransformer|None=None, MODEL_NAME:str|None='sonoisa/sentence-bert-base-ja-mean-tokens-v2') -> None:
        self.query_theme = query_theme
        self.ds = ds
        if model:
            self.model = model
        else:
            self.model = SentenceTransformer(MODEL_NAME)

    def get_embeddings(self,texts:list[str])-> torch.Tensor:
        """
        texts : データベースとなる文章の集合.

        文章の埋め込み表現を獲得.
        """
        return self.model.encode(texts,convert_to_tensor=True)

    def get_response_text_ids(self,query_embeddings:torch.Tensor, top_k:int=10) -> list:
        """
        query_embeddings : クエリテーマの埋め込み表現.
        top_k : 関連度の高いうちの上から幾つ持ってくるか.

        レスポンステキストを持ってくる.
        まだ、分類はされていない.
        """

        # sentence_transformersのutil.sematic_searchで.
        # データベース上からクエリテーマとのコサイン類似度上位top_k個のレスポンステキストのidを取得.
        response_id_score = util.semantic_search(query_embeddings,self.ds.embeddings,top_k=top_k)

        # sematic_searchの戻り値はtop_k個の('corpus_id','score')のリストとなっている.
        # それをクエリテーマごとにcorpus_idのみのリストに変換.
        response_ids:list[list[int]] = []
        for i,theme in enumerate(response_id_score):
            response_ids.append([])
            for id_score in theme:
                response_ids[i].append(id_score['corpus_id'])
        return response_ids

    def do(self,top_k:int=100,threshold:int=0.75,return_text:bool=True,return_id:bool=False)-> list[int]:
        """
        top_k : 幾つのレスポンステキストを獲得のか.\
            デフォルトでは100となっている.
        threshold : レスポンステキストを分類する際にどれだけ類似していればいいのか.\
            -1から1が指定できるはずだが、0.5以下にすると何故か処理が終わらないので0.6以上が推奨.\
            デフォルトでは0.75となっている.
        return_text : 戻り値を文章とするのか.\
            デフォルトではTrueとなっている.
        return_id : 戻り値をデータベース上での文章のidとするのか.\
            デフォルトではFalseとなっている.\
            return_textよりもこちらが優先される.

        レスポンステキストを取得し、分類を行った結果を返す.
        """

        # クエリテーマとデータベース上の文章の埋め込み表現を獲得.
        query_embeddings = self.get_embeddings(self.query_theme)
        if not len(self.ds.embeddings):
            self.ds.embeddings = self.get_embeddings(self.ds.body)
        
        # レスポンステキストの埋め込み表現の獲得.
        response_ids = self.get_response_text_ids(query_embeddings,top_k)
        response_embeddings = []
        for i,theme in enumerate(response_ids):
            response_embeddings.append([])
            for id in theme:
                response_embeddings[i].append(self.ds.embeddings[id].tolist())
        response_embeddings = torch.tensor(response_embeddings)

        # レスポンステキストの分類.
        classified_text_ids = []
        for i,theme_embeddings in enumerate(response_embeddings):
            classified_text_ids.append(util.community_detection(theme_embeddings,threshold=threshold,min_community_size=1))
        
        # util.community_detectionの戻り値はレスポンステキスト内でのidとなっている.
        # それをreturn_textとreturn_idによってデータベース上でのidまたは文章のどちらかに変換.
        # POINT : I abominate the code here because there are so many statements.
        classified_response:dict[str,list[list[int|str]]] = dict()
        for i,theme in enumerate(classified_text_ids):
            classified_response[self.query_theme[i]] = []
            for j,community in enumerate(theme):
                classified_response[self.query_theme[i]].append([])
                for id in community:
                    if return_id:
                        classified_response[self.query_theme[i]][j].append(response_ids[i][id])
                    elif return_text:
                        classified_response[self.query_theme[i]][j].append(self.ds.body[response_ids[i][id]])

        return classified_response