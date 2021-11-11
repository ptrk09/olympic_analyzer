from django.shortcuts import render
from analyzer.olap import connect_olap_model
from olympic.settings import BASE_DIR, KEYWORDS_FILE_PATH, OLAP_MODEL_PATH, HEADER_ALIASES_PATH
import analyzer.handler_requests as hr
import analyzer.browser as databrowser


def index(request):
    if request.method == 'POST':
        keywords_dict = request.POST
        if keywords_dict:
            browser = databrowser.OlapBrowser()
            data = browser.get_olap_data(KEYWORDS_FILE_PATH, keywords_dict)
            data["header"] = browser.set_aliases_header(data["header"], HEADER_ALIASES_PATH)
            return render(request, 'analyzer/view_table.html', data)


