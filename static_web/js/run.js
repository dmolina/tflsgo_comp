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
        available_algs: [],
        algs: [],
        alg_name: 'PROPOSAL',
        error: '',
        dimension: '',
        report_name: '',
        tables: {},
        figures: {},
        figures_js: '',
        figure_divs: {},
        libcharts: 'hc',
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
                else {
                    self.dimension = '';
                }

                if (self.reports.length==1) {
                    self.report_name = self.reports[0].description;
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
        appendFiguresHv: function() {
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
            $('figures img').addClass('img-fluid');
        },
        appendFiguresHighcharts: function(plots) {
            var self = this;
            div = document.getElementById('figures');
            // Empty the div
            div.innerHTML = '';
            var num = plots.length;
            var next_plot = 1;

            for (var plot_i = 0; plot_i < num; plot_i++) {
                info_plot = plots[plot_i];
                new_row = document.createElement("div");
                new_row.className = "row";
                title = info_plot['title'];

                if (title) {
                    new_title = document.createElement("h2");
                    new_title.append(document.createTextNode(title));
                    new_row.append(new_title);
                    div.append(new_row);
                    new_row = document.createElement("div");
                    new_row.className = "row";
                }

                num_row = info_plot['num'];

                for (var i = 1; i <= num_row; i++) {
                    new_fig = document.createElement("div");
                    new_fig.id = 'figures' +next_plot;
                    next_plot += 1;
                    new_fig.className = "col col-sd-12";
                    new_row.append(new_fig);
                }

                div.append(new_row);
            }
            $('#figures_link').focus();
            $('figures img').addClass('img-fluid');
        },
       sendData: function(e) {
           var self = this;
           var mobile = false;
           self.error = '';
           init_process();

        $.ajax(make_ajax_info('compare', e)
              ).done(function(data) {
                self.error = '';
                if (data['error']) {
                    self.error = data['error'];
                    $("label#file").focus();
                }
                  else {
                    self.error = '';
                    self.tables = data['tables'];
                    charts = data['type'];
                    if (charts == 'hv') {
                        self.figure_divs = data['divs'];
                        self.figures_js = data['js'];
                        self.appendFiguresHv();
                    }
                      else if (charts == 'highcharts') {
                        figures = data['figures'];
                        plots_info = data['figures_info'];
                        self.appendFiguresHighcharts(plots_info);
                        var num = figures.length;

                        for (var i = 0; i < num; i++) {
                            var src = "new Highcharts.Chart(" +figures[i] +");";
                            eval(src);
                        }
                    }
                    else {
                        self.error = "chart type '" +charts +"' unknown";
                    }
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
