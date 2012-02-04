=============
pystol
=============
:Author:	Jun Kimura
:Licence: 	MIT
:Description:   指定したファイル群からインデックスを作成し、指定した文字列を含むファイルを抽出します。

Require
-----------
::

 Python2.x>=2.6
 python-magic
 watchdog
		
Install
------------
::

 python setup.py install
	
Usage
------------
::

	$ python pystol.py -k start  			# run server
	$ python pystol.py -a /home/user/doc 	        # add directory path in Index
	$ python pystol.py -f "todo"			# search string in Index
	 /home/user/doc/hobby.txt			# show matching file list
	 /home/user/doc/shopping.txt
	 ...
	 ...
	$ python pystol.py -k stop		        # stop server


	