# Telegram alert system

This is the script, which can send the alerts in automated (using CI/CD) mode. It checks the key metrics each 15 minutes and compares this value with the mean value of the same 15-minute interval for last 10 days. In case of deviation for more than 3σ, it sends the alert message, plot and link to the real-time dashboard.

## The script has following steps:  
* Importing libraries
* Connecting to telegram bot
* Connecting to database
* Extracting the key metrics from data
* Checking if the significant deviation took place
* Making and sending the message and plots in case of alert.

## This script covers such metrics as:
* Number of active feed users
* Number of active messenger users
* Number of likes 
* Number of views
* CTR
* Number of sent messages
