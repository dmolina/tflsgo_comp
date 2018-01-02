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
        available_algs: [],
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
            console.log("onChangedDimension");
            $.ajax({
                url: base_url +'/algs/' +self.selected +'/' +self.dimension,
                method: 'GET'}
            ).done(function(data) {
                    console.log('algs');
                    console.log(data['algs']);
                    self.available_algs = data['algs'];
                    self.error = data['error'];
            });
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
            eval(self.figures_js);
        },
       sendData: function(e) {
           var self = this;
           $.ajax(make_ajax_info('compare', e)
            ).done(function(data) {
                self.error = '';
                if (data['error']) {
                    self.error = data['error'];
                    $("label#file").focus();
                    return;
                }
                self.tables = data['tables'];
                self.figure_divs = data['divs'];
                self.figures_js = data['js'];
                self.appendFigures();
            })
               .fail(function(data){
                   self.error = process_fail(data);
                });
        }
    }

});
