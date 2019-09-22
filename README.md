# Items Catalog
### For Full Stack Web Developer Nano-degree program  
<a href="https://www.udacity.com/">
  <img src="https://s3-us-west-1.amazonaws.com/udacity-content/rebrand/svg/logo.min.svg" width="100" alt="Udacity logo">
</a>

The Application provides a list of items within a variety of categories as well as provide a user registration and authentication system. Registered users will have the ability to post, edit and delete their own items.


## Table of Contents

- [Table of Contents](#table-of-contents)
- [Intro](#intro)
- [Instructions](#instructions)
- [Authentication](#authentication)
- [DB ORM](#db-orm)
- [APIs](#apis)
- [To Dos](#to-dos)

## Intro

The content of application revolves around sports items which are listed based on their category.
After logging in, the users can post their items under the corresponding category.
It is possible to add new categories (reserved for admins only -- **details below** )

For testing  [Vagrant](https://www.vagrantup.com/) and [VirtualBox](https://www.virtualbox.org/wiki/Download_Old_Builds_5_1) to install and manage the VM can be used


## Instructions

The current version application supports Python 2.6 and 2.7 while there are  ongoing efforts to support Python 3.4+

### Virtual Env

 1. **install virtualenv for python 2+**
    `[server$] pip install virtualenv`
    
 2. **Navigate to your site's directory. This is where you'll create the new virtual environment:**
`[server]$ cd $HOME/example.com`
 3. **Create the virtual environment at the same time you specify the version of Python you wish to use.**
`[server]$ virtualenv -p /path/to/python-2.6+/python my_project`
  
 4. **Run the following to activate this new virtual environment:**
`[server]$ source my_project/bin/activate`
  
  5. **Clone the Items Catalog App repo.**
  `[server]$ git clone https://github.com/andreony/Items-Catalog.git <project-name>`

6. **install dependencies to virtual env** 
`[server]$ pip install -r requirements.txt `

7. **Run the development server which will start the app at http://localhost:5000**
`[server]$ python application.py`

### Authentication

The app supports 2 login providers: 
1. <img src="https://proxy.duckduckgo.com/iu/?u=https%3A%2F%2F1000logos.net%2Fwp-content%2Fuploads%2F2016%2F11%2Fgoogle-plus-logo.jpg&f=1&nofb=1" width=100px;> 
 ---
2. <img src="https://sguru.org/wp-content/uploads/2018/02/facebook_logos_PNG19762.png" width=80px;>
---
You can enable Admin login (**development only**) by setting the APP_DEV_STATUS setting variable to True (**False by default**), then the Admin login will be available at http://localhost:5000/admin
This will speed up dev testing, completely removing the need to login each time the dev server refreshes

**NOTE**:  Make sure you disable the admin user login in production

## DB-ORM

The ORM is supported by [SQLAlchemy](https://www.sqlalchemy.org/) and the application includes an SQLite3 db which can be used for testing.
For production, it's recommended to switch to a more robust database (eg: postgreSQL, MySQL, etc.)

**NOTE:** If the db engine in changed, make sure you reflect the changes in the models.py file:
from `engine = create_engine(
  'sqlite:///catalog_items2.db',
  connect_args={'check_same_thread': False}
)` to the appropriate db engine

## APIs
In order to enable facebook and google plus authentication, you must add 2 your apis keys as follows:
1. Google - API key in file `client_secrets.json`
2. Facebook - API kei in file `fb_client_secrets.json`

**Example:**
`{
  "web": {
    "app_id": "{app_id_key}",
    "app_secret": "{app_secret}"
  }
}`


## To Dos
- Support additional authentication providers e.g. Amazon, GitHub etc.
- Menu item to allow authenticated users to see all their posts 
- Use jQuery modals for authentication instead of redirecting to login page
- Include Pictures to the Catalog Item model and use them in the views

