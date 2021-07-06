///
/// @file
/// @brief 地名接尾辞クラスの定義。
/// @author 国立情報学研究所
///
/// Copyright (c)2010-2013, NII
///

#ifndef _SUFFIX_H
#define _SUFFIX_H

#include <string>

namespace geonlp
{
	/// @brief 地名接尾辞を表すクラス。
	class Suffix {
	private:
		/// 表層形
		std::string surface;
		
		/// 読み
		std::string yomi;
		
		/// 発音
		std::string pronunciation;
		
	public:
		/// @brief デフォルトコンストラクタ。
		Suffix(){};
		
		/// @brief コンストラクタ。
		///
		/// @arg @c s 表層形
		/// @arg @c y 読み
		/// @arg @c p 発音
		Suffix( const std::string &s, const std::string& y, const std::string& p): surface(s), yomi(y), pronunciation(p){};
		
		/// 表層形を得る。
		inline const std::string get_surface() const;
		
		/// 表層形を設定する。
		inline void set_surface(std::string value);
		
		/// 読みを得る。
		inline const std::string get_yomi() const;
		
		/// 読みを設定する。
		inline void set_yomi(std::string value);
		
		/// 発音を得る。
		inline const std::string get_pronunciation() const;
		
		/// 発音を設定する。
		inline void set_pronunciation(std::string value);
		
	};
	
	inline const std::string Suffix::get_surface() const {
		return surface;
	}

	inline void Suffix::set_surface(std::string value) {
		surface = value;
	}

	inline const std::string Suffix::get_yomi() const {
		return yomi;
	}

	inline void Suffix::set_yomi(std::string value) {
		yomi = value;
	}

	inline const std::string Suffix::get_pronunciation() const {
		return pronunciation;
	}

	inline void Suffix::set_pronunciation(std::string value) {
		pronunciation = value;
	}

}
#endif
