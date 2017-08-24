import sys
import json
import requests
from jinja2 import Environment, FileSystemLoader 
from weasyprint import HTML

# performs API calls to obtain the sonar qube analysis results for the given componentKey (project)
def performComponentKeyAPICall(componentKey):
    url = "http://localhost:9000/api/issues/search?componentKeys="+componentKey+"&statuses=OPEN&ps=1"
    r = requests.get(url)
    json_data = json.loads(r.text)
    if json_data['total'] == 0: 
        print ("no data returned - no report will be generated")
    else:
        print ("found " + str(json_data['total']) + " issues. a report will be generated...")
        json_all = "["

        # GET ALL ISSUS (max. 500) OF TYPE BUG
        url = "http://localhost:9000/api/issues/search?componentKeys="+componentKey+"&statuses=OPEN&ps=500&types=BUG"
        r = requests.get(url)
        json_bugs = json.loads(r.text)
        if json_bugs['total'] > 0:
            print ("found " + str(json_bugs['total']) + " issues of type BUG")
            json_bugs = filterJSON(json_bugs)
            json_all += json_bugs

        # GET ALL ISSUES (max. 500) OF TYPE CODE_SMELL
        url = "http://localhost:9000/api/issues/search?componentKeys="+componentKey+"&statuses=OPEN&ps=500&types=CODE_SMELL"
        r = requests.get(url) 
        json_codesmells = json.loads(r.text)
        if json_codesmells['total'] > 0: 
            print ("found " + str(json_codesmells['total']) + " issues of type CODE_SMELL")
            json_codesmells = filterJSON(json_codesmells)
            if json_all != '[':
                json_all += ","
            json_all += json_codesmells

        # GET ALL ISSUES (max. 500) OF TYPE VULNERABILITY
        url = "http://localhost:9000/api/issues/search?componentKeys="+componentKey+"&statuses=OPEN&ps=500&types=VULNERABILITY"
        r = requests.get(url)
        json_vulnerabilities = json.loads(r.text)
        if json_vulnerabilities['total'] > 0:
            print ("found " + str(json_vulnerabilities['total']) + " issues of type VULNERABILITY")
            json_vulnerabilities = filterJSON(json_vulnerabilities)
            if json_all != "[": 
                json_all += ","
            json_all += json_vulnerabilities
        json_all += "]"


        # GENERATE PDF
        JSONtoPDF(json_all, componentKey)


# filters the json response of the API call
def filterJSON(json_data):
    # select only the 'issues' key for filtering
    json_issues = json_data['issues']
    # we will filter the json with this keys for the target output
    json_keySet = ['component', 'author', 'message', 'effort', 'type']

    json_filtered = ''
    for issue in json_issues:
        json_filtered += '{'
        for key, value in issue.items():
         if key in json_keySet:
            # remove " in values - otherwise the target JSON is not valid 
            value = value.replace('"', '')
            value = value.replace("'", '')
            strAttr = '\"'+key+'\":\"'+value+'\",'
            json_filtered += strAttr
         if key == 'textRange':
             for k,v in  value.items():
                 if k == 'startLine' or k == 'endLine':
                    strAttr = '\"'+str(k)+'\":'+str(v)+','
                    json_filtered += strAttr
        # removes the last , from the JSON string
        json_filtered = json_filtered[:-1]
        json_filtered += '},'
    # removes the last , from the JSON string
    json_filtered = json_filtered[:-1]
    return json_filtered


def JSONtoPDF(json_str, componentKey):
    json_data = json.loads(json_str)
    html_issues = ""

    for i in json_data:
        html_issues += "<tr>"
        if 'type' in i:
            html_issues += "<td>" + i['type'] + "</td>"
        else:
            html_issues += "<td></td>"
        if 'component' in i:
            component = i['component']
            component = component.split(":")[-1]
            html_issues += "<td>" + component + "</td>"
        else:
            html_issues += "<td></td>"
        if 'startLine' in i:
            html_issues += "<td>" + str(i['startLine']) + "</td>"
        else:
            html_issues += "<td></td>"
        if 'endLine' in i:
            html_issues += "<td>" + str(i['endLine']) + "</td>"
        else:
            html_issues += "<td></td>"
        if 'message' in i:
            html_issues += "<td>" + i['message'] + "</td>"
        else:
            html_issues += "<td></td>"
        if 'author' in i:
            html_issues += "<td>" + i['author'] + "</td>"
        else:
            html_issues += "<td></td>"
        if 'effort' in i:
            html_issues += "<td>" + i['effort'] + "</td>"
        else:
            html_issues += "<td></td>"
        html_issues += "</tr>"

    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template("reportTemplate.html")
    template_vars = {"project" : componentKey, "issue_table" : html_issues}
    html_out = template.render(template_vars)
    HTML(string=html_out).write_pdf("report.pdf", stylesheets=["style.css"])

def main():
    argvLen = len(sys.argv)
    if argvLen == 2:
        componentKey = sys.argv[1]
        print("API call for project: " + componentKey + " will be executed")
        performComponentKeyAPICall(componentKey)
    else:
        print("please specify a project for the analysis report.")

if __name__ == "__main__":
    main()
