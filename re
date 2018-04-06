Python用" \\\\ "表示正则表达式中的" \ "。原始字符串(raw string) 用'r'作为字符串的前缀，如 r"\n"：表示两个字符"\"和"n"

元字符：”\”+”A”表示开头（r’\A’==’\\A’）
\A       Matches only at the start of the string.
\Z       Matches only at the end of the string.
\b       Matches the empty string, but only at the start or end of a word.
\B       Matches the empty string, but not at the start or end of a word.
\d       Matches any decimal digit; equivalent to the set [0-9]
\D       Matches any non-digit character; equivalent to [^\d].
\s       Matches any whitespace character; equivalent to [ \t\n\r\f\v]
\S       Matches any non-whitespace character; equivalent to [^\s].
\w       Matches any alphanumeric character; equivalent to [a-zA-Z0-9_]
\W       Matches the complement of \w.
\\        Matches a literal backslash.

(?P<name>...)  The substring matched by the group is accessible by name.
(?P=name)     Matches the text matched earlier by the group named name. 
(?=...)  Matches if ... matches next, but doesn't consume the string.     #前向匹配
(?!...)  Matches if ... doesn't match next.
(?<=...) Matches if preceded by ... (must be fixed length).        #后向匹配
(?<!...) Matches if not preceded by ... (must be fixed length).

不贪婪的限定符 *?、+?、?? 或 {m,n}?，尽可能匹配小的文本

compile
re.compile(pattern[, flags])
编译正则表达式，返回RegexObject对象，供 match() 和 search() 这两个函数使用。
re 所定义的 flag 包括：
re.I 忽略大小写（ignorecase）
re.L 表示特殊字符集 \w, \W, \b, \B, \s, \S 依赖于当前环境（locale）
re.M 多行模式（multiline）
re.S 即为’ . ’并且包括换行符在内的任意字符（’ . ’不包括换行符）
re.U 表示特殊字符集 \w, \W, \b, \B, \d, \D, \s, \S 依赖于 Unicode 字符属性数据库
re.X 为了增加可读性，忽略空格和’ # ’后面的注释
prog = re.compile(pattern) 
result = prog.match(string)
等同于result = re.match(pattern, string)

search
re.search(pattern, string[, flags])
在字符串中查找匹配正则表达式模式的位置，返回 MatchObject 的实例，如果没有找到匹配的位置，则返回 None。
若 regex 是已编译好的正则表达式对象，regex.search(string, 0, 50) 等同于 regex.search(string[:50])
>>> pattern = re.compile("a") 
>>> pattern.search("abcde")     # Match at index 0 
>>> pattern.search("abcde", 1)   # No match;
group（）用来提出分组截获的字符串，group(0)指所有匹配的内容，group(1)指第一个()匹配内容
#!/usr/bin/python
import re
line = "Cats are smarter than dogs";
matchObj = re.search( '(.*) are(\.*)', line, re.M|re.I)
if matchObj:
  print "matchObj.group() : ", matchObj.group()
  print "matchObj.group(1) : ", matchObj.group(1)
  print "matchObj.group(2) : ", matchObj.group(2)
else:
  print "No match!!"
#matchObj.group(): Cats are
 matchObj.group(1) : Cats
 matchObj.group(2) :
match
re.match(pattern, string[, flags])
字符串的开头是否能匹配正则表达式
对于 RegexObject，有：match(string[, pos[, endpos]])
match() 函数只在字符串的开始位置尝试匹配正则表达式，而 search() 函数是扫描整个字符串来查找匹配。如果想要搜索整个字符串来寻找匹配，应当用 search()

split
re.split(pattern, string[, maxsplit=0, flags=0])
将字符串匹配正则表达式的部分割开并返回一个list。如果用括号将正则表达式括起来，那么匹配的字符串也会被列入到list中返回
对 RegexObject，有函数：split(string[, maxsplit=0])
>>> re.split('\W+', 'Words, words, words.') 
['Words', 'words', 'words', ''] 
>>> re.split('(\W+)', 'Words, words, words.') 
['Words', ', ', 'words', ', ', 'words', '.', ''] 
>>> re.split('\W+', 'Words, words, words.', 1) 
['Words', 'words, words.']

findall
re.findall(pattern, string[, flags])
在字符串中找到正则表达式所匹配的所有子串，并组成一个列表返回
对RegexObject 有：findall(string[, pos[, endpos]])
>>> re.findall(r"\d+","12a32bc43jf3") 
['12', '32', '43', '3']
finditer（类似findall）
re.finditer(pattern, string[, flags])
在字符串中找到正则表达式所匹配的所有子串，并组成一个迭代器返回 
RegexObject 有：finditer(string[, pos[, endpos]])
>>> it = re.finditer(r"\d+","12a32bc43jf3") 
>>> for match in it: 
              print match.group()
12 
32 
43 
3
sub
re.sub(pattern, repl, string[, count, flags])
在字符串 string 中找到匹配正则表达式 pattern 的所有子串，用另一个字符串 repl 进行替换。如果没有找到匹配 pattern 的串，则返回未被修改的 string。Repl 既可以是字符串也可以是一个函数
对于 RegexObject 有：sub(repl, string[, count=0])
>>> p = re.compile( '(one|two|three)') 
>>> p.sub( 'num', 'one word two words three words') 
'num word num words num words'
同样可以用以下方法，并指定 count 为 1（只替换第一个）
>>> p.sub( 'num', ' one word two words three words', count=1)
' num word two words three words'

subn
re.subn(pattern, repl, string[, count, flags])
该函数的功能和 sub() 相同，但它还返回新的字符串以及替换的次数
对RegexObject 有：subn(repl, string[, count=0])

re.escape(string)
对字符串中的非字母数字进行转义
re.purge()
清空缓存中的正则表达式
