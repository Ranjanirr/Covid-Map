from studies import *
import cherrypy
import os

class Mapper(object):
    @cherrypy.expose
    def index(self):
        f, d = dataIO.getLatestCSVFile("Data/", "ctp-")
        if d != datetime.date.today():
            dataIO.initData(update=True, prompt=False)

            userParams["selectedStates"] = [k for k in list(statePopulation.keys()) if k not in statesToExclude]
            userParams["outputType"] = "js"
            userParams["jsfile"] = "public/js/results.js"

            print("\nTabulating for states\n", userParams["selectedStates"])
            tabulateStateResults(userParams["selectedStates"])

        return open("index.html")


if __name__ == "__main__":

    conf = {
        '/': {
            'tools.sessions.on': True,
            'tools.staticdir.root': os.path.abspath(os.getcwd())
        },
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './public'
        }
    }
    print("Starting Server!!")
    cherrypy.quickstart(Mapper(), '/', conf)


