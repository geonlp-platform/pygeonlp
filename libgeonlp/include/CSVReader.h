/**
 * CSV�t�@�C���ǂݍ��݃N���X
 * @author      ��k�L�X
 * @version     CVS $Id: CSVReader.h,v 1.1 2008/03/26 12:45:24 tamamo Exp $
 * @license     BSD license:
 * Copyright (c) 2008, Taipei Cat Project
 * All rights reserved.
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *
 *     * Redistributions of source code must retain the above copyright
 *       notice, this list of conditions and the following disclaimer.
 *     * Redistributions in binary form must reproduce the above copyright
 *       notice, this list of conditions and the following disclaimer in the
 *       documentation and/or other materials provided with the distribution.
 *     * Neither the name of the Taipei Cat Project nor the
 *       names of its contributors may be used to endorse or promote products
 *       derived from this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS ``AS IS'' AND ANY
 * EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
 * WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 * DISCLAIMED. IN NO EVENT SHALL THE REGENTS AND CONTRIBUTORS BE LIABLE FOR ANY
 * DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
 * (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
 * LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
 * ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 * SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */

#ifndef _CSVREADER_H__
#define _CSVREADER_H__

#include <string>
#include <vector>
#include <fstream>
using namespace std;

#define DEFAULT_SEPARATOR	','
#define DEFAULT_QUOTE_CHARACTER	'"'

class CSVReader
{
public:

	/**
	 * �R���X�g���N�^
	 * @param stream �t�@�C���X�g���[��
	 * @comment �Z�p���[�^(,), �G���N�I�[�g(")
	 */
	CSVReader(fstream& stream);

	/**
	 * �R���X�g���N�^
	 * @param stream �t�@�C���X�g���[��
	 * @param sep �Z�p���[�^
 	 * @comment �G���N�I�[�g(")
	 */
	CSVReader(fstream& stream, const char sep);

	/**
	 * �R���X�g���N�^
	 * @param stream �t�@�C���X�g���[��
	 * @param sep �Z�p���[�^
 	 * @param quo �G���N�I�[�g
	 */
	CSVReader(fstream& stream, const char sep, const char quo);

	/**
	 * �f�X�g���N�^
	 */
	virtual ~CSVReader(void);

	/**
	 * CSV�t�@�C�����P�s�ǂݍ���ŁA�������Ĕz��ŕԂ��܂��B
	 * @param tokens �g�[�N��(OUT)
	 * @return 0:���� -1:EOF
	 */
	int Read(vector<string>& tokens);

	/**
	 * �t�@�C���X�g���[�����N���[�Y���܂��B
	 * @return 0:���� -1:�ُ�
	 */
	int Close(void);

private:

	/**
	 * �t�@�C������P�s�ǂݍ��݂܂��B
	 * @param line �s�f�[�^
	 * @return >=0�F�ǂݍ��񂾃f�[�^�� -1�FEOF
	 */
	int GetNextLine(string& line);

	/**
	 * �f�[�^���p�[�X���܂��B
	 * @param nextLine �s�f�[�^
	 * @param tokens �p�[�X�����f�[�^�̔z��(OUT)
	 * @return 0
	 */
	int Parse(string& nextLine, vector<string>& tokens);

	std::fstream* pstream;
	char separator;
	char quote;

};

#endif
