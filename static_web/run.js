// var base_url = "http://localhost:8000";
var base_url = "";

function addCode(code){
    var JS= document.createElement('script');
    JS.text= code;
    document.body.appendChild(JS);
}

var app = new Vue({
    el: '#app',
    data: {
        benchmarks: {},
        alg_name: '',
        selected: -1,
        available_algs: {},
        algs: [],
        error: '',
        dimension: '',
        report_name: '',
        tables: {},
        figures: {},
        figures_js: '',
        figure_divs: {}
    },
    mounted: function() {
        var self = this;
        $.ajax({
            url: base_url +'/benchmarks',
            method: 'GET',
            success: function(data) {
                self.benchmarks = data['benchmarks'];
            }
        });
    },
    methods: {
        onChangedBenchmark: function() {
            var self = this;
            var dimensions = self.benchmarks[self.selected].dimensions;
            var reports = self.benchmarks[self.selected].reports;

            if (dimensions.length==1) {
                self.dimension = dimensions[0];
                self.onChangedDimension();
            }
            if (reports.length==1) {
                self.report_name = reports[0].name;
            }
        },
        onChangedDimension: function() {
            var self = this;
            $.ajax({
                url: base_url +'/algs/' +self.selected +'/' +self.dimension,
                method: 'GET',
                sucess: function(data) {
                    self.available_algs = data['algs'];
                    self.error = data['error'];
                }
            });
        },
        runjs: function() {
            console.log("run");
            addCode(this.figures_js);
        },
        appendFigures: function() {
            var self = this;
            div = document.getElementById('figures');
            // Empty the div
            div.innerHTML = '';

            for (fi in self.figure_divs) {
                fig = self.figure_divs[fi];
                new_title = document.createElement("h2");
                new_title.append(document.createTextNode(fi));
                div.append(new_title);
                div.innerHTML += fig;
            }
            console.log("appendFigures Final div:");
            console.log(div.innerHTML);
            console.log(self.figures_js);
            eval(self.figures_js);
            // js = document.getElementById('figures_js');
            // console.log(self.figures_js);
            // setTimeout(self.runjs, 1000);
        },
       sendData: function(e) {
            var self = this;
            e.preventDefault();
            var formData = new FormData(e.target);

            $.ajax({
                url: base_url +'/compare',
                type: 'POST',
                data: formData,
                dataType: 'json',
                cache: false,
                contentType: false,
                processData: false
            }).done(function(data) {
                console.log('done');
                console.log(data);
                self.error = '';
                if (data['error']) {
                    self.error = data['error'];
                    $("label#file").focus();
                    return;
                }
                self.tables = data['tables'];
                self.figures = data['figures'];
                self.figure_divs = data['divs'];
                self.figures_js = data['js'];
                self.appendFigures();
            })
               .fail(function(data){
                   console.log('failed');
                   console.log(data.responseJSON);
                   error = data.responseJSON['message'];
                   console.log(error);

                   for (name in error) {
                       self.error = name +': ' +error[name];
                   }
                });
        }
    }

});
