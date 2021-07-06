///
/// @file
/// @brief 形態素情報クラスNodeの定義。
/// @author 国立情報学研究所
///
/// Copyright (c)2010-2013, NII
///

#ifndef _NODE_H
#define _NODE_H

#include <string>
#include <vector>
#include "picojson.h"

namespace geonlp
{
	
  /// @brief 形態素情報クラス。
  ///
  /// MeCabにより得られる形態素情報と同等。
  class Node {
  protected:
    /// 形態素の文字列情報(表層形)。
    std::string surface;

    /// MeCab::Nodeの持つfeature。CSV で表記された素性情報。
    std::string feature;

  private:
    /// 品詞
    std::string partOfSpeech;

    /// 品詞細分類１
    std::string subclassification1;

    /// 品詞細分類２
    std::string subclassification2;

    /// 品詞細分類３／地名語ID
    std::string subclassification3;

    /// 活用形
    std::string conjugatedForm;

    /// 活用型
    std::string conjugationType;

    /// 原形
    std::string originalForm;

    /// 読み
    std::string yomi;

    /// 発音
    std::string pronunciation;
	
    static const std::string delim;

  public:
    /// @brief コンストラクタ。
    ///
    /// 引数に与えられたfeatureを素性情報に分解し、各メンバに設定する。
    /// @arg @c surface 形態素の文字列情報(表層形)
    /// @arg @c feature MeCab::Nodeの持つfeature。CSV で表記された素性情報。
    Node( const std::string& surface, const std::string& feature);

    /// コピーコンストラクタ
    Node(const Node& n) {
      this->surface = n.surface;
      this->feature = n.feature;
      this->partOfSpeech = n.partOfSpeech;
      this->subclassification1 = n.subclassification1;
      this->subclassification2 = n.subclassification2;
      this->subclassification3 = n.subclassification3;
      this->conjugatedForm = n.conjugatedForm;
      this->conjugationType = n.conjugationType;
      this->originalForm = n.originalForm;
      this->yomi = n.yomi;
      this->pronunciation = n.pronunciation;
    }


    /// 形態素の文字列情報(表層形)を得る。
    inline const std::string get_surface() const;

    /// 形態素の文字列情報(表層形)を設定する。
    inline void set_surface(std::string value);

    /// 品詞を得る。
    inline const std::string get_partOfSpeech() const;

    /// 品詞を設定する。
    inline void set_partOfSpeech(std::string value);

    /// 品詞細分類１を得る。
    inline const std::string get_subclassification1() const;

    /// 品詞細分類１を設定する。
    inline void set_subclassification1(std::string value);

    /// 品詞細分類２を得る。
    inline const std::string get_subclassification2() const;

    /// 品詞細分類２を設定する。
    inline void set_subclassification2(std::string value);

    /// 品詞細分類３／地名語IDを得る。
    inline const std::string get_subclassification3() const;

    /// 品詞細分類３／地名語IDを設定する。
    inline void set_subclassification3(std::string value);

    /// 活用形を得る。
    inline const std::string get_conjugatedForm() const;

    /// 活用形を設定する。
    inline void set_conjugatedForm(std::string value);

    /// 活用型を得る。
    inline const std::string get_conjugationType() const;

    /// 活用型を設定する。
    inline void set_conjugationType(std::string value);

    /// 原形を得る。
    inline const std::string get_originalForm() const;

    /// 原形を設定する。
    inline void set_originalForm(std::string value);

    /// 読みを得る。
    inline const std::string get_yomi() const;

    /// 読みを設定する。
    inline void set_yomi(std::string value);

    /// 発音を得る。
    inline const std::string get_pronunciation() const;

    /// 発音を設定する。
    inline void set_pronunciation(std::string value);

    /// picojson::object を返す。
    virtual picojson::object toObject() const;

    /// デバグ用のテキスト表記を得る。
    virtual std::string toString() const;

    virtual ~Node() {}
		
  };
	
  inline const std::string Node::get_surface() const {
    return surface;
  }

  inline void Node::set_surface(std::string value) {
    surface = value;
  }

  inline const std::string Node::get_partOfSpeech() const {
    return partOfSpeech;
  }

  inline void Node::set_partOfSpeech(std::string value) {
    partOfSpeech = value;
  }

  inline const std::string Node::get_subclassification1() const {
    return subclassification1;
  }

  inline void Node::set_subclassification1(std::string value) {
    subclassification1 = value;
  }

  inline const std::string Node::get_subclassification2() const {
    return subclassification2;
  }

  inline void Node::set_subclassification2(std::string value) {
    subclassification2 = value;
  }

  inline const std::string Node::get_subclassification3() const {
    return subclassification3;
  }

  inline void Node::set_subclassification3(std::string value) {
    subclassification3 = value;
  }

  inline const std::string Node::get_conjugatedForm() const {
    return conjugatedForm;
  }

  inline void Node::set_conjugatedForm(std::string value) {
    conjugatedForm = value;
  }

  inline const std::string Node::get_conjugationType() const {
    return conjugationType;
  }

  inline void Node::set_conjugationType(std::string value) {
    conjugationType = value;
  }

  inline const std::string Node::get_originalForm() const {
    return originalForm;
  }

  inline void Node::set_originalForm(std::string value) {
    originalForm = value;
  }

  inline const std::string Node::get_yomi() const {
    return yomi;
  }

  inline void Node::set_yomi(std::string value) {
    yomi = value;
  }

  inline const std::string Node::get_pronunciation() const {
    return pronunciation;
  }

  inline void Node::set_pronunciation(std::string value) {
    pronunciation = value;
  }

}
#endif
