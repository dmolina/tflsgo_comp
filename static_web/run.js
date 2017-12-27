var base_url = "http://localhost:8000";

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
        report: {},
        tables: {},
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
                self.report = reports[0];
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
                console.log(data);
                self.error = '';
                if (data['error']) {
                    self.error = data['error'];
                    $("label#file").focus();
                }
                self.tables = data['tables'];
            })
               .fail(function(data){
                   console.log('hola');
                console.log(data);
                error = data['error'];

                for (name in error) {
                    self.error += error[name];
                }
                });
        }
    }

});
