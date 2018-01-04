function addCode(code){
    var JS= document.createElement('script');
    JS.text= code;
    document.body.appendChild(JS);
}

var app = new Vue({
    el: '#app',
    data: {
        benchmark: {},
        dimensions: [],
        reports: [],
        alg_name: '',
        available_algs: [],
        algs: [],
        error: '',
        dimension: '',
        report_name: '',
        tables: {},
        figures: {},
        figures_js: '',
        figure_divs: {},
        mobile: false
    },
    mounted:  function() {
        if (/Mobi/.test(navigator.userAgent)) {
            this.mobile = true;
        }
    },
    methods: {
        enumerate: function(elements) {
            var results = [];
            elements.forEach(function(e, ind) {
                results.push([ind, e]);
            });
            return results;
        },
        onChangedBenchmark: function(bench) {
            var self = this;
            self.dimensions = [];
            self.reports = [];
            self.available_algs = [];

            if (bench['id']) {
                self.dimensions = bench['dimensions'];
                self.reports = bench['reports'];

                if (self.dimensions.length==1) {
                    self.dimension = self.dimensions[0];
                    self.onChangedDimension();
                }
                if (self.reports.length==1) {
                    self.report_name = self.reports[0].name;
                }
            }
        },
        onChangedDimension: function() {
            var self = this;
            $.ajax({
                url: 'algs/' +self.benchmark['id'] +'/' +self.dimension,
                method: 'GET'}
            ).done(function(data) {
                    self.available_algs = data['algs'];
                    self.error = data['error'];
            });
        },
        appendFigures: function() {
            var self = this;
            div = document.getElementById('figures');
            // Empty the div
            div.innerHTML = '<a href="" id="figures_link"></a>';

            for (fi in self.figure_divs) {
                fig = self.figure_divs[fi];
                new_title = document.createElement("h2");
                new_title.append(document.createTextNode(fi));
                div.append(new_title);
                div.innerHTML += fig;
            }
            $('#figures_link').focus();
            eval(self.figures_js);
        },
       sendData: function(e) {
           var self = this;
           var mobile = false;

           init_process();

        $.ajax(make_ajax_info('compare', e)
            ).done(function(data) {
                self.error = '';
                if (data['error']) {
                    self.error = data['error'];
                    $("label#file").focus();
                }
                else {
                    self.tables = data['tables'];
                    self.figure_divs = data['divs'];
                    self.figures_js = data['js'];
                    self.appendFigures();
                }
                finish_process();
            })
               .fail(function(data){
                   self.error = process_fail(data);
                   finish_process();
                });
        }
    }

});
