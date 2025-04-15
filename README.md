# EasyTaskManager

To install the cd in the project directory and run "docker-compose up -d --build"
This will create dockers:
backend - python API
db - MySQL database (permanent volume can be increased by adding it to the last raw of docker-compose file.yml)
interface - the TypeScript interface will be installed on npm >18
nginx - interface/nginx.conf
redis - necessary for saving sessions
