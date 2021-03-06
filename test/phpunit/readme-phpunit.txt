Running PHP Unit Tests
===============================================================================

These tests are for the PHP scripts in the /web directory.

First install phpunit. For details see 
http://phpunit.de/manual/current/en/automating-tests.html. I used apt-get instead 
of the instructions there.

To run the tests, cd to the directory containing the tests (eg test/phpunit) and
use the command:

$ phpunit NameOfTest.php

To run the entire suite of unit tests cd to the directory above the tests and use
the command

$ phpunit phpunit/

The second 'phpunit/' is the name of the directory containing the tests.

Many of the 'unit tests' actually hit the database just as the actual web access
does. Make sure that the database_utils.php script has the right value for 
database password.

Coverage Analysis
===============================================================================
Install Xdebug and then run the phpunit coverage tool:

$ sudo pecl install xdebug

Find the php.ini file
$ php -i | grep 'Configuration File'

Find the location of the xdebug.so file
find / -name 'xdebug.so' 2> /dev/null

Edit the php.ini fild
$ sudo vi /etc/php5/cli/php.in
..
zend_extension="/<PROPER_LOCATIONA>/xdebug.so"

Generate the coverage report
$ phpunit --coverage-html ./report phpunit/

