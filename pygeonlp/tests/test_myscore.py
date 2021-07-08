import pygeonlp.api as api
from pygeonlp.api.linker import RankedResults
from pygeonlp.api.scoring import ScoringClass

api.init()


class MyScoringClass(ScoringClass):

    def path_score(self, path):
        """
        パスの中に指定した文字列で始まる固有名クラスの地名語が
        存在する数をスコアとして返すスコアリングメソッド。

        Parameters
        ----------
        path : list of Node
            解析結果候補のパス表現。
        self.options : str
            カウントする固有名クラスの先頭文字列

        Returns
        -------
        int
            target_class にマッチする固有名クラスを持つ地名語数。
        """
        if not isinstance(self.options, str):
            raise RuntimeError(
                "オプションパラメータは文字列で指定してください。")

        target_class = self.options
        score = 0
        geowords = RankedResults.collect_geowords(path)
        for geoword in geowords:
            if geoword.prop['ne_class'].startswith(target_class):
                score += 1

        return score


if __name__ == '__main__':
    print("'鉄道施設' が多い候補を優先した場合。")
    print(api.geoparse(
        '和歌山市は晴れ。',
        scoring_class=MyScoringClass, scoring_options='鉄道施設', ))
    print("'市区町村' が多い候補を優先した場合。")
    print(api.geoparse(
        '和歌山市は晴れ。',
        scoring_class=MyScoringClass, scoring_options='市区町村'))
