# -*- coding: utf-8 -*-
"""
Created on Tue May 30 16:36:55 2017

@author: Rick
"""

from flask import Flask, request, render_template
from Bio import Entrez, Medline

Entrez.email = "history.user@example.com"

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return render_template( './index.html' )

@app.route("/documenten", methods=["GET"])
def doc():
    return render_template( './documenten.html' )

@app.route("/getlist", methods=["GET"])
def getlist():
    with open("static/assets/list/lijst.txt", "r") as f:
        content = []
        for regel in f:
            if regel is "\n":
                None
            else:
                content.append(regel.rstrip())
    return render_template("getlist.html", content="\n".join(content))

@app.route("/savelist", methods=["POST"])
def savelist():
    content = request.form["lijst"]
    output = open("static/assets/list/lijst.txt", mode="w") 
    output.write(content)        
    return render_template("savelist.html", content=content)

@app.route("/results", methods=["POST"])
def results():
    query = request.form["query"]
    date1 = request.form["date1"]
    date2 = request.form["date2"]

    bestand = open("static/assets/list/lijst.txt", mode="r")

    bl = makeList(bestand)
    makeJson(bl, query, date1, date2)

    return render_template('./results.html', query=query, date1=date1, date2=date2)

def makeList(bestand):
    begripLijst = []

    for regel in bestand:
        if regel in ("\n", "\r\n"):
            None
        else:
            regel = regel.strip()
            begripLijst.append(regel)
            
    return begripLijst

def makeJson(bl, query, date1, date2):
    output = open("static/assets/resultaten.json",'w', newline="\r\n")
    count2 = 0
    count3 = 0
    length = len(bl)-1

    output.write("""{ "nodes":[""")
    output.write("""{"id":"n", "loaded":true, "style":{ "fillColor": "rgba(236,46,46,0.8)", "label":\""""+query+"\"""}},\n""")

    for res in range(len(bl)):
        search_results = Entrez.read(Entrez.esearch(db="pubmed", term= query+" AND "+bl[count2]+" "+str(date1)+":"+str(date2)+" [PDAT]", datetype="pdat", usehistory="y"))
        count = int(search_results["Count"])

        if count2 == length:
            output.write("""{"id":"n"""+str(count2)+"""", "loaded":true, "style":{ "fillColor": "rgba(47,195,47,0.8)", "label":\""""+bl[count2]+""" """+str(count)+""" resultaten\"}}\n""")
        else:
            output.write("""{"id":"n"""+str(count2)+"""", "loaded":true, "style":{ "fillColor": "rgba(47,195,47,0.8)", "label":\""""+bl[count2]+""" """+str(count)+""" resultaten\"}},\n""")

        print("Found {0} results between {1} and {2}".format(count, query, bl[count2]))

        count2+=1
    output.write("],")

    output.write("""\"links\":[""")
    for sco in range(len(bl)):
        if count3 == length:
            output.write("""{"id":"e"""+str(count3)+"""", "from":"n", "to":"n"""+str(count3)+"""", "style":{"fillColor":"rgba(236,46,46,1)", "toDecoration":"arrow"}}\n""")
        else:
            output.write("""{"id":"e"""+str(count3)+"""", "from":"n", "to":"n"""+str(count3)+"""", "style":{"fillColor":"rgba(236,46,46,1)", "toDecoration":"arrow"}},\n""")
        count3+=1
    output.write("]}")

@app.route("/table", methods=["POST"])
def table():
    query = request.form["query"]
    date1 = request.form["date1"]
    date2 = request.form["date2"]
    count=0

    term=query+" AND "+str(date1)+":"+str(date2)+" [PDAT]"

    search_results = Entrez.read(Entrez.esearch(db="pubmed", term=term, datetype="pdat", usehistory="y", RetMax=100000))

    ids = search_results['IdList']

    h = Entrez.efetch(db='pubmed', id=ids, rettype='medline', retmode='text')
    records = Medline.parse(h)

    table = ""
    for record in records:
        ti = record.get('TI', '-')
        ot = record.get('OT','-')
        au = record.get('AU', '-')
        dp = record.get('DP', '-')
        table+="<tr><td><div class=\"comment more\">{0}</div></td><td><div class=\"comment more\">{1}</div></td><td><div class=\"comment more\">{2}</div></td><td>{3}</td><td><a href=https://www.ncbi.nlm.nih.gov/pubmed/?term=""{4}"">{4}</a></td></tr>".format(ti, ', '.join(ot), ', '.join(au), dp, str(ids[count]))

    return render_template("articles.html", table=table)

if __name__ == "__main__":
    app.run()
