///
/// @file
/// @brief 形態素情報拡張クラスの定義。
/// @author 国立情報学研究所
///
/// Copyright (c)2010-2013, NII
///

#ifndef _NODEEXT_H
#define _NODEEXT_H

#include <string>
#include <vector>
#include "Node.h"
#include "PHBSDefs.h"
#include "Suffix.h"

namespace geonlp
{	
	/// @brief 形態素情報拡張クラス。
	///
	/// MeCabによる解析結果として得られた形態素情報に対し、地名語候補を得るために付加情報を与えたクラス。
	class NodeExt: public Node {
	private:
		/// 地名語の先頭となり得るか。
		bool bHead;
		
		/// 地名語の部分となり得るか。
		bool bBody;

		/// 地名接頭辞となり得るか。
		bool bPrefix;
		
		/// 地名接尾辞となり得るか(地名接尾辞を末尾に含むか)。
		bool bSuffix;

                /// 地名語に先行しない単語か。
                bool bAntileader;
		
		/// 単独で地名語になり得るか。
		bool bSingle;

                /// 単独の場合、地名語以外の可能性を検討するか。
                bool bAlternative;
		
		/// 対応する地名接尾辞(bSuffix==trueの場合)
		Suffix suffix;

                /// 地名語に後続しない語となり得るか。
                bool bStop;
		
	public:
		/// @brief コンストラクタ。
		/// 
		/// @arg @c node 形態素情報
		NodeExt( const Node& node): Node(node), bHead(false), bBody(false), bPrefix(false), bSuffix(false), bSingle(false), bStop(false) {};
		
		// 形態素が地名語のどの部分になり得るか判定する。
		void evaluatePossibility(const PHBSDefs& phbsdef, bool nextIsHead);

		/// @brief 地名語の先頭となり得るか。
		/// @retval true なり得る。
		/// @retval false なり得ない。
		inline bool canBeHead() const { return bHead;};

	  /// @brief 地名語の先頭としての評価を指定する
	  inline void setBeHead(bool f) { this->bHead = f; }
		
		/// @brief 地名語の部分となり得るか。
		/// @retval true なり得る。
		/// @retval false なり得ない。
		inline bool canBeBody() const { return bBody;};
		
	  /// @brief 地名語に後続しない語となり得るか。
	  /// @retval true なり得る。
	  /// @retval false なり得ない。
	  inline bool canBeStop() const { return bStop;};
		
		/// @brief 地名接頭辞となり得るか。
		/// @retval true なり得る。
		/// @retval false なり得ない。
		inline bool canBePrefix() { return bPrefix;};
		
		/// @brief 地名接尾辞となり得るか(地名接尾辞を末尾に含むか)。
		/// @retval true なり得る(含む)。
		/// @retval false なり得ない(含まない)。
		inline bool canBeSuffix() { return bSuffix;};
		
		/// @brief 地名語に先行しない単語か。
		/// @retval true 先行しない。
		/// @retval false 先行する可能性がある。
		inline bool canBeAntileader() { return bAntileader;};
		
	  /// @brief 地名語に先行する単語かどうかを指定する
	  inline void setBeAntileader(bool f) { this->bAntileader = f; }

		/// @brief 単独で地名語となり得るか。
		/// @retval true なり得る。
		/// @retval false なり得ない。
		inline bool canBeSingleGeoword() { return bSingle;};
		
	  /// @brief 一語の場合、地名語以外の可能性を併記するか。
	  /// @retval 併記しない場合は空白。
	  /// @retval "人名"など、の併記する文字列。
	  std::string getAlternativeValue(const PHBSDefs& phbsdef) const;
		
		/// @brief 対応する地名接尾辞を得る。(bSuffix==trueの場合)
		inline const Suffix get_suffix() const { return suffix;};
		
		/// @brief デバグ用のテキスト表記を得る。
	  std::string toString() const;

	};
	
}
#endif
