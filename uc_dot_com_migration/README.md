# README

* add here the code for urbancode.com migration

## overview of "license version conventions" used and which I need to check for getting the correct version for latestversion and for sorting (float value)

* standard is filename-versionnumber( \d+\.{1}\d+ ).extension
* com.ibm.udeploy.plugin.ram.zip
  * no version number in the filename 
  * no latest version also use "0.0" -> 0.0 for sort
* ibm-ucd-agent-script-package-6.2.0.2.zip 
  * version number is at end
  * version number is not default format
  * find all numbers after last "-" and remove after first "." every other non digit character
  * -> "6.2.0.2" -> 6.202
* db2-application-deployment-template-package-v5.zip -> use v5, convert to 5.0
* DB2forzOS1.0.zip -> use 1.0 -> convert to 1.0
* cics-42.20210716-1150.zip -> use 42.20210716 -> same for sort
*  