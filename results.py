#!/bin/python
import os, sys, json, datetime, re

data = dict()
data_fn = "results.json"

def load_data():
    global data
    if (os.path.exists(data_fn)):
        f = open(data_fn)
        data = json.load(f)
        f.close()
    if ("tests" not in data.keys()):
        data["tests"] = []

def save_data():
    global data
    f = open(data_fn, "w")
    json.dump(data, f)
    f.close()

def add_test_results(test, result):
    global data
    load_data()
    idx = -1
    # find previous result
    for i in range(len(data["tests"])):
        if (data["tests"][i]["name"] == test):
            idx = i
            break
    res = dict()
    res["name"] = test
    res["result"] = result
    res["last_run"] = datetime.datetime.now().isoformat()
    if (idx == -1):
        data["tests"].append(res)
    else:
        data["tests"][idx] = res
    save_data()

def create_html():
    global data
    load_data()
    f = open("results.html", "w")
    s = ('''<html>
    <head>
        <meta charset="utf-8"/>
        <title>Tests and Implementation Report</title>
        <style>
            #tests-table {
                border: 1px solid #cccccc;
                color: #313131;
                font-size: 14px;
                width: 100%
            }
            #tests-table th, #tests-table td {
                padding: 5px;
                border: 1px solid #E6E6E6;
                text-align: left
            }
            #tests-table th {
                font-weight: bold
            }
            .sortable {
                cursor: pointer;
            }
            .sort-icon {
                font-size: 0px;
                float: left;
                margin-right: 5px;
                margin-top: 5px;
                /*triangle*/
                width: 0;
                height: 0;
                border-left: 8px solid transparent;
                border-right: 8px solid transparent;
            }
            .inactive .sort-icon {
                /*finish triangle*/
                border-top: 8px solid #E6E6E6;
            }

            .asc.active .sort-icon {
                /*finish triangle*/
                border-bottom: 8px solid #999;
            }
            .desc.active .sort-icon {
                /*finish triangle*/
                border-top: 8px solid #999;
            }
        </style>
        <script>
            function toArray(iter) {
                if (iter === null) {
                    return null;
                }
                return Array.prototype.slice.call(iter);
            }

            function find(selector, elem) {
                if (!elem) {
                    elem = document;
                }
                return elem.querySelector(selector);
            }

            function find_all(selector, elem) {
                if (!elem) {
                    elem = document;
                }
                return toArray(elem.querySelectorAll(selector));
            }

            function reset_sort_headers() {
                find_all('.sort-icon').forEach(function(elem) {
                    elem.parentNode.removeChild(elem);
                });
                find_all('.sortable').forEach(function(elem) {
                    var icon = document.createElement("div");
                    icon.className = "sort-icon";
                    icon.textContent = "vvv";
                    elem.insertBefore(icon, elem.firstChild);
                    elem.classList.remove("desc", "active");
                    elem.classList.add("asc", "inactive");
                });
            }

            function toggle_sort_states(elem) {
                //if active, toggle between asc and desc
                if (elem.classList.contains('active')) {
                    elem.classList.toggle('asc');
                    elem.classList.toggle('desc');
                }

                //if inactive, reset all other functions and add ascending active
                if (elem.classList.contains('inactive')) {
                    reset_sort_headers();
                    elem.classList.remove('inactive');
                    elem.classList.add('active');
                }
            }

            function key_alpha(col_index) {
                return function(elem) {
                    return elem.childNodes[0].childNodes[col_index].firstChild.data.toLowerCase();
                };
            }

            function sort_column(elem) {
                toggle_sort_states(elem);
                name = ((elem).closest('table')).id;
                var colIndex = toArray(elem.parentNode.childNodes).indexOf(elem);
                var key;
                if (elem.classList.contains('numeric')) {
                    key = key_num;
                } else if (elem.classList.contains('result')) {
                    key = key_result;
                } else {
                    key = key_alpha;
                }
                sort_table(elem, key(colIndex), name);
            }

            function sort(items, key_func, reversed) {
                var sort_array = items.map(function(item, i) {
                    return [key_func(item), i];
                });
                var multiplier = reversed ? -1 : 1;

                sort_array.sort(function(a, b) {
                    var key_a = a[0];
                    var key_b = b[0];
                    return multiplier * (key_a >= key_b ? 1 : -1);
                });

                return sort_array.map(function(item) {
                    var index = item[1];
                    return items[index];
                });
            }

            function sort_table(clicked, key_func, tname) {
                var rows = find_all('.'+tname+'-row');
                var reversed = !clicked.classList.contains('asc');
                var sorted_rows = sort(rows, key_func, reversed);
                /* Whole table is removed here because browsers acts much slower
                * when appending existing elements.
                */
                var thead = document.getElementById(tname+"-head");
                document.getElementById(tname).remove();
                var parent = document.createElement("table");
                parent.id = tname;
                parent.appendChild(thead);
                sorted_rows.forEach(function(elem) {
                    parent.appendChild(elem);
                });
                document.getElementsByTagName(tname+"-BODY")[0].appendChild(parent);
            }

            function init () {
                reset_sort_headers();
                toggle_sort_states(find('.initial-sort'));
                find_all('.sortable').forEach(function(elem) {
                    elem.addEventListener("click",
                                        function(event) {
                                            sort_column(elem);
                                        }, false)
                });
            };
        </script
    </head>
    <body onLoad="init()">
        <h2>Test results</h2>
        <tests-table-body>
        <table id="tests-table">
            <thead id="tests-table-head">
                <tr><th class="sortable name initial-sort" col="tname">Name</th><th class="sortable name initial-sort" col="tcode">Result</th><th class="sortable name initial-sort" col="tdata">Last run</th></tr>
            </thead>
''')
    f.write(s)
    for test in data["tests"]:
        s = '<tbody class="tests-table-row"><tr><td class="col-tname">{0}</td><td class="col-tcode">{1}</td><td class="col-tdata">{2}</td></tr></tbody>\n'
        f.write(s.format(test["name"], test["result"], test["last_run"]))
    s = ('''        </table>
        <h2>Timing reports</h2>
        <table id="tests-table">
            <thead id="tests-table-head">
                <tr><th>Model</th><th>Fmax</th></tr>
            </thead>\n''')
    f.write(s)
    for fm in data["timings"]["Fmax"]:
        s = '<tbody class="tests-table-row"><tr><td>{0}</td><td>{1}</td></tr></tbody>\n'
        f.write(s.format(fm["Model"], fm["fmax"]))
    s = ('''        </table>
    </body>
</html>''')
    f.write(s)
    f.close()

def parse_quartus(path):
    global data
    load_data()
    f = open(path + ".sta.rpt")
    lines = []
    timings = dict()
    timings_fmax = []
    for line in f:
        lines.append(line)
    for i in range(len(lines)):
        model = re.search("\S+ \d+mV \d+C", lines[i])
        if (model):
            res = re.search("\d+\.\d+ MHz", lines[i+4])
            if (res):
                fm = dict()
                fm["Model"] = model.group()
                fm["fmax"] = res.group()
                timings_fmax.append(fm)
    f.close()
    timings["Fmax"] = timings_fmax
    data["timings"] = timings
    save_data()

argc = len(sys.argv)
data_fn = sys.argv[1]
op = sys.argv[2]
if ((argc == 5) and (op == "add")):
    add_test_results(sys.argv[3], sys.argv[4])
elif ((argc == 3) and (op == "html")):
    create_html()
elif ((argc == 4) and (op == "parse_quartus")):
    parse_quartus(sys.argv[3])
else:
    print("Invalid parameters!")
