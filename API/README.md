# SomeProject

## Installation (Ubuntu >= 16.04)

### PHP + Apache + MySQL

	$ sudo apt install mysql-server
	$ sudo apt install php7
	$ sudo apt install apache2
	$ sudo apt install libapache2-mod-php7
	$ sudo apt install php7-mysql
	$ sudo service apache2 restart
	
### Create database

Connect to mysql

	$ sudo mysql -p -u root
	
Execute next queries for creating database
	

	> CREATE DATABASE `someproject` CHARACTER SET utf8 COLLATE utf8_general_ci;
	> CREATE USER 'someproject_u'@'localhost' IDENTIFIED BY 'someproject_p';
	> GRANT ALL PRIVILEGES ON someproject.* TO 'someproject_u'@'localhost' WITH GRANT OPTION;
	> FLUSH PRIVILEGES;
	> exit;

Apply sql file for creating structure of tables:

	$ mysql -u root -p someproject < someproject.sql


### Install PHP scripts

	$ ln -s `pwd`/www /var/www/html/someproject
	$ sudo cp www/config.php.example www/config.php 
	
## Where see

	http://localhost/someproject/
