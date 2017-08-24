# Sonar Reporter 
this Python tool performs an API call to your sonar cube instance and converts the response to a PDF <br>

## Installation 
* create a virtualenv <br>
  `virtualenv --system-site-packages ./venv` <br>
* switch to it by sourcing the activate file: <br>
  `. ./venv/bin/activate`
* install the dependencies: <br>
  ```
  pip install WeasyPrint
  pip install requests
  pip install jinja2
  ```

## Execution
execute in virtualenv (see above) <br> 
* execution for a project: <br>
  `python3 sonar_reporter.py myproject` <br>
* after execution a report named analysis.pdf will be created 


## Use Cases 

### create a report with a Jenkins task 
* first check out the project in your jenkins workspace (/var/lib/jenkins/workspace) <br>
* create a build task for your project which has been analysed with Sonar Qube <br> 
  - this build task should be executed after the Sonar Qube analysis 
  - build task -> invoke shell script: <br> 
  ```
  cd $WORKSPACE
  cd $WORKSPACE
  cd ..
  cd sonar_report_generator
  virtualenv --system-site-packages ./venv
  . ./venv/bin/activate
  pip install WeasyPrint
  pip install requests
  pip install jinja2

  python sonar_reporter.py $JOB_BASE_NAME
  mv report.pdf $WORKSPACE  
  ```
  
  - hint: don't forget to set the the location of $PYTHON3_HOME in the jenkins environment settings <br> 
