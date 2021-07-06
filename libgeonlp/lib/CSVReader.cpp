/**
 * CSVファイル読み込みクラス
 * @author      台北猫々
 * @version     CVS $Id: CSVReader.cpp,v 1.1 2008/03/26 12:45:24 tamamo Exp $
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

#include "CSVReader.h"

CSVReader::CSVReader(fstream& stream):
  pstream(&stream), separator(DEFAULT_SEPARATOR),
  quote(DEFAULT_QUOTE_CHARACTER) {}

CSVReader::CSVReader(fstream& stream, const char sep):
  pstream(&stream), separator(sep), quote(DEFAULT_QUOTE_CHARACTER) {}

CSVReader::CSVReader(fstream& stream, const char sep, const char quo):
  pstream(&stream), separator(sep), quote(quo) {}

CSVReader::~CSVReader(void) {}

int CSVReader::Read(vector<string>& tokens) {
	tokens.clear();

	string nextLine;
	if( GetNextLine(nextLine)<=0 ) {
		return -1;
	}
	Parse(nextLine, tokens);
	return 0;
}

int CSVReader::GetNextLine(string& line) {

	if( !pstream || pstream->eof() ) {
		return -1;
	}
	std::getline( *pstream, line );
	return (int)line.length();
}

int CSVReader::Parse(string& nextLine, vector<string>& tokens) {
	string token;
	bool interQuotes = false;
	do {
		if (interQuotes) {
			token += '\n';
			if (GetNextLine(nextLine)<0) {
				break;
			}
		}
		
		for (int i = 0; i < (int)nextLine.length(); i++) {

			char c = nextLine.at(i);
			if (c == quote) {
               	if( interQuotes
               	    && (int)nextLine.length() > (i+1)
               	    && nextLine.at(i+1) == quote ){
               		token += nextLine.at(i+1);
               		i++;
               	}else{
               		interQuotes = !interQuotes;
               		if(i>2 
               			&& nextLine.at(i-1) != separator
               			&& (int)nextLine.length()>(i+1) 
               			&& nextLine.at(i+1) != separator
               		){
               			token += c;
               		}
               	}
			} else if (c == separator && !interQuotes) {
				tokens.push_back(token);
				token.clear();
			} else {
				token += c;
			}
		}
	} while (interQuotes);
	tokens.push_back(token);
	return 0;
}

/**
 * ファイルストリームをクローズします。
 * @return 0:正常 -1:異常
 */
int CSVReader::Close(void) {
	if(pstream) {
		pstream->close();
		pstream = NULL;
	}
	return 0;
}

