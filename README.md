

## What is this?

This project is based on Alpine Linux, the official nginx image and an nginx module made by Google that provides brotli compression, which also is made by Google.

## How to use this image

As this project is based on the official nginx image look for instructions there. In addition to the standard configuration directives, you'll be able to use the brotli module specific ones, see here for official documentation

### Nginx Configuration

    brotli on;
    brotli_comp_level 6;
    brotli_types application/eot application/x-otf application/font application/x-perl application/font-sfnt application/x-ttf application/javascript
                font/eot application/json font/ttf application/opentype font/otf application/otf font/opentype application/pkcs7-mime image/svg+xml
                application/truetype text/css application/ttf text/csv application/vnd.ms-fontobject text/html application/xhtml+xml text/javascript
                application/xml text/js application/xml+rss text/plain application/x-font-opentype text/richtext application/x-font-truetype 
                text/tab-separated-values application/x-font-ttf text/xml application/x-httpd-cgi text/x-script application/x-javascript
                text/x-component application/x-mpegurl text/x-java-source application/x-opentype
                ;

More information are available: https://github.com/google/ngx_brotli

## Credits

 - This repository is a fork of https://github.com/fholzer/docker-nginx-brotli adjusted with latest changes from the official docker image.