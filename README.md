# broken-urls-finder

Python script that runs in k8s on a cronjob to find all broken links after deployment. (example: 404, 500, 503 and etc.)

Results are being posted in the slack channel. (template is included) 

Slack channel with alerts: TBD (up to you)

## Why use this tool?

This tools is ideal for checking the error list (404, 500, 503 and etc.) whenever these kind of errors arise for a website.

For SEO purposes, it is very bad to have lots of 404 erros exist in your site, and it also could irritate users.

These errors may arrise as a result of a desing change of a website, website migration, or a small change in an htaccess file.

When the script finishes, it shows you a summary of how many urls were broken and what environment was affected (DEV/PROD).

## Slack channel with alerts: #tech-dead-links-alerts

## Future plans
- In the future, refactor this script to make it multithreaded, so a large list of urls can get checked faster
- Link depth limit
